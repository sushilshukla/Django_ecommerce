from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
from django.conf import settings

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        CUSTOMER = "customer","Customer"
        VENDOR   = "vendor","Vendor"
        ADMIN    = "admin","Admin"
    email         = models.EmailField(max_length=254, unique=True)
    first_name    = models.CharField(max_length=80, blank=True)
    last_name     = models.CharField(max_length=80, blank=True)
    phone         = models.CharField(max_length=10, unique=True, blank=True, null=True)
    role          = models.CharField(max_length=10, choices=Role.choices, default=Role.CUSTOMER)
    avatar        = models.ImageField(upload_to="avatar/%Y/%m",null=True,blank=True)
    is_active     = models.BooleanField(default=True)
    is_staff      = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD    = "email"
    REQUIRED_FIELDS   = ["first_name"]
    
    class Meta:
        indexes = [models.Index(fields=["role","is_active"])]
        
    def __str__(self):
        return self.email
    
class Address(models.Model):
    class Label(models.TextChoices):
        HOME = "home","HOME"
        WORK = "work","WORK"
        OTHER = "other","OTHER"
        
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name = "addresses"
    )
    
    label = models.CharField(
        max_length=10,
        choices=Label.choices,
        default = Label.HOME
    )
    
    full_name               =   models.CharField(max_length=150)
    phone                   =   models.CharField(max_length=15) 
    line1                   =   models.CharField(max_length=255)
    line2                   =   models.CharField(max_length=255,blank=True)
    city                    =   models.CharField(max_length=100)
    state                   =   models.CharField(max_length=100)
    postal_code             =   models.CharField(max_length=10)
    country                 =   models.CharField(max_length=2, default='IN')
    
    is_default_shipping    =   models.BooleanField(default=False)
    is_default_billing      =   models.BooleanField(default=False)
    
    created_at              =   models.DateTimeField(auto_now_add=True)
    updated_at              =   models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes             =   [
            models.Index(fields=["user","is_default_shipping"]),
            models.Index(fields=["user","is_default_billing"]),
            ]
    
    def __str__(self):
        return f"{self.full_name}-{self.city}"