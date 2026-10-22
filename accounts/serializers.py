from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
#from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from .models import User,Address
import re

class RegisterSerializer(serializers.ModelSerializer):
    password     = serializers.CharField(write_only=True, min_length=8, validators = [validate_password])
    password2    = serializers.CharField(write_only=True)  
    
    class Meta:
        model   = User
        fields  = ["id","email","first_name","last_name","phone","role","password","password2"]
        
        
    def validate_email(self,value):
        value = value.strip().lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This mail is already registered")
        return value
    
    def validate_role(self,value):
        if value == User.Role.ADMIN:
            raise serializers.ValidationError("You cannot register as admin.")
        return value
    
    def validate_phone(self,value):
        return value or None
    
    def validate(self,attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Password do not match"})
        return attrs
    
    def create(self,validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(**validated_data)
    
    
class LoginSerializer(serializers.Serializer):
     
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self,attrs):
        email = attrs.get("email","").strip().lower()
        password = attrs.get("password")
        
        user = authenticate(
            request = self.context.get("request"),
            username = email,
            password=password
        )
       
        if user is None:
            raise serializers.ValidationError("Invlalid email or Password ")
        
        if not user.is_active:
            raise serializers.ValidationError("This account is deactivated")
        
        attrs['user'] = user
        return attrs
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "avatar",
            "role",
            "is_email_verified",
            "is_phone_verified",
            "date_joined",
            "updated_at"
            
        )
        
        read_only_fields = (
            "id",
            "email",
            "role",
            "is_email_verified",
            "is_phone_verified",
            "date_joined",
            "updated_at"
            
        )
        
    def validate_phone(self,value):
        return value or None
            
            
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only = True,trim_whitespace=False)
    new_password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    new_password2 = serializers.CharField(write_only=True, trim_whitespace  = False)
    
    def validate_old_password(self,value):
        user = self.context["request"].user
        
        if not user.check_password(value):
            raise serializers.ValidationError("Current Password is incorrect")
        return value
    
    def validate(self, attrs):
        new_password = attrs['new_password']
        new_password2 = attrs['new_password2']
        user = self.context["request"].user
        
        if new_password != new_password2:
            raise serializers.ValidationError({
                "new_password2": "New password do not match"
            })
        
        if user.check_password(new_password):
            raise serializers.ValidationError({
                "new_password": "New password must be different from current password"
            })
            
        validate_password(new_password,user=user)
        
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.strip().lower()


class ResetPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        trim_whitespace=False,
    )
    new_password2 = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({
                "new_password2": "New password do not match"
            })
        validate_password(attrs["new_password"])
        return attrs
    
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            
            "id",
            "label",
            "full_name",
            "phone",
            "line1",
            "line2",
            "city",
            "state",
            "postal_code",
            "country",
            "is_default_shipping",
            "is_default_billing",
            "created_at",
            "updated_at"
        )
        
        read_only_fields = (
            "id",
            "is_default_shipping",
            "is_default_billing",
            "created_at",
            "updated_at"
        )
        
    def validate_phone(self,value):
        value = value.strip()
        
        if not re.fullmatch(r"\+?[1-9]\d{7,14}", value):
            raise serializers.ValidationError("Enter a valid phone number")
        return value
    
    def validate_country(self,value):
        return value.strip().upper()
    
    def validate(self, attrs):
        country = attrs.get(
            "country",
            getattr(self.instance,"country","IN"),
        )
        
        postal_code = attrs.get(
            "postal_code",
            getattr(self.instance,"postal_code",""),
            )
        
        if country == "IN" and not re.fullmatch(
            r"[1-9]\d{5}",
            postal_code,
        ):
            raise serializers.ValidationError({"postal_code":"Enter a 6 digit Indian Postal Code"})
        
        return attrs


class SetDefaultAddressSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(
        choices=["shipping", "billing", "both"]
    )
                