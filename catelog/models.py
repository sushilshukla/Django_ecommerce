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
