from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80,unique=True)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete= models.PROTECT,
        related_name="children",
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order","name"]
        indexes = [

            models.Index(fields=["slug"]),
            models.Index(fields=["is_active","sort_order"]),
        ]

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80, unique=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order","name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active","sort_order"])
        ]
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160,unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category,
        on_delete = models.PROTECT,
        related_name = "products",
    )
    brand = models.ForeignKey(
        Brand,
        on_delete = models.PROTECT,
        related_name = "products",
    )
    mrp = models.DecimalField(max_digits=10, decimal_places = 2)
    price = models.DecimalField(max_digits=10, decimal_places  = 2)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [

            models.Index(fields=["slug"]),
            models.Index(fields=["is_active","category"]),
            models.Index(fields=["brand"]),
        ]
    def __str__(self):
        return self.name