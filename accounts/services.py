from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db import transaction
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .models import Address, User
from .exceptions import DuplicateAddressError, InvalidPasswordResetError


def normalize_text(value):
    return " ".join(value.strip().split())

@transaction.atomic
def create_address(*,user, validated_data):
    user.__class__.objects.select_for_update().get(pk=user.pk)
    
    data = validated_data.copy()
    data['full_name']   = normalize_text(data['full_name'])
    data['phone']       = data["phone"].strip()
    data['line1']       = normalize_text(data['line1'])
    data["line2"]       = normalize_text(data.get("line2", ""))
    data['city']        = normalize_text(data['city'])
    data['state']       = normalize_text(data['state'])
    data['postal_code'] = normalize_text(data['postal_code'])
    data['country']     = normalize_text(data['country'])
    data["country"]     = data.get("country", "IN").strip().upper()
    
    duplicate_exist = Address.objects.filter(
        user=user,
        full_name__iexact = data["full_name"],
        phone = data["phone"],
        line1__iexact = data["line1"],
        line2__iexact = data["line2"],
        city__iexact = data["city"],
        state__iexact = data["state"],
        postal_code = data["postal_code"],
        country__iexact = data["country"],
    ).exists()
    
    
    if duplicate_exist:
        raise DuplicateAddressError()
        
    is_first_address  = not Address.objects.filter(
        user=user
    ).exists()
    
  
    
    if is_first_address:
        data['is_default_shipping'] = True
        data['is_default_billing'] = True
        
    return Address.objects.create(
        user=user,
        **data,
    )
    
    
@transaction.atomic
def update_address(*,user,address,validated_data):
    user.__class__.objects.select_for_update().get(pk=user.pk)
    
    address = Address.objects.select_for_update().get(pk=address.pk,user=user,)
    data = validated_data.copy()
    
    for field in (
        'full_name',
        'line1',
        'line2',
        'city',
        'state'
    ):
        if field in data:
            data[field] = normalize_text(data[field])
    if "phone" in data:
        data["phone"] = data["phone"].strip()
    if "postal_code" in data:
        data["postal_code"] = data["postal_code"].strip()
    if "country" in data:
        data["country"] = data["country"].strip().upper()
    
    merged = {

        "full_name":data.get("full_name",address.full_name),
        "phone":data.get("phone",address.phone),
        "line1":data.get("line1",address.line1),
        "line2":data.get("line2",address.line2),
        "city":data.get("city",address.city),
        "state":data.get("state",address.state),
        "postal_code":data.get("postal_code",address.postal_code),
        "country":data.get("country",address.country),
    }

    duplicate_exist = Address.objects.filter(
        user=user,
        full_name__iexact=merged["full_name"],
        phone=merged["phone"],
        line1__iexact=merged["line1"],
        line2__iexact=merged["line2"],
        city__iexact=merged["city"],
        state__iexact=merged["state"],
        postal_code=merged["postal_code"],
        country__iexact=merged["country"],
    ).exclude(pk=address.pk).exists()
    
    if duplicate_exist:
        raise DuplicateAddressError()
        
    for field,value in data.items():
        setattr(address,field,value)

    address.save()
    return address


@transaction.atomic
def set_default_address(*,user,address,kind):
    user.__class__.objects.select_for_update().get(pk=user.pk)   
    address = Address.objects.select_for_update().get(
        pk=address.pk,
        user=user,
        )

    if kind in ("shipping","both"):
        Address.objects.filter(
            user=user,
            is_default_shipping=True,
        ).exclude(pk=address.pk).update(is_default_shipping=False)
        address.is_default_shipping = True

    if kind in ("billing","both"):
        Address.objects.filter(
            user=user,
            is_default_billing=True,
        ).exclude(pk=address.pk).update(is_default_billing=False)
        address.is_default_billing = True

    address.save(
        update_fields=[
            "is_default_shipping",
            "is_default_billing",
            "updated_at",
        ]
    )

    return address


def _is_admin_user(user):
    return user.role == User.Role.ADMIN or user.is_staff


def _blacklist_user_tokens(user):
    try:
        from rest_framework_simplejwt.token_blacklist.models import (
            BlacklistedToken,
            OutstandingToken,
        )
    except Exception:
        return

    for outstanding in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=outstanding)


def request_admin_password_reset(*, email):
    response = {
        "success": True,
        "message": "If this email belongs to an admin account, reset instructions were sent.",
    }

    user = User.objects.filter(email=email, is_active=True).first()
    if user is None or not _is_admin_user(user):
        return response

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = PasswordResetTokenGenerator().make_token(user)

    send_mail(
        subject="Admin password reset",
        message=(
            "Use this uid and token with POST /api/reset-password/.\n"
            f"uid: {uid}\n"
            f"token: {token}\n"
        ),
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@localhost"),
        recipient_list=[user.email],
        fail_silently=True,
    )

    if settings.DEBUG:
        response["data"] = {
            "uid": uid,
            "token": token,
        }

    return response


@transaction.atomic
def reset_admin_password(*, uid, token, new_password):
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.select_for_update().get(pk=user_id, is_active=True)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        raise InvalidPasswordResetError()

    if not _is_admin_user(user):
        raise InvalidPasswordResetError()

    if not PasswordResetTokenGenerator().check_token(user, token):
        raise InvalidPasswordResetError()

    user.set_password(new_password)
    user.save(update_fields=["password", "updated_at"])
    _blacklist_user_tokens(user)
    return user