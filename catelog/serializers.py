from rest_framework import serializers
from django.utils.text import slugify
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "parent",
            "is_active",
            "sort_order",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
        extra_kwargs = {
            "slug": {"required": False},
        }

    def validate_name(self, value):
        return " ".join(value.strip().split())

    def validate(self, attrs):
        name = attrs.get("name") or getattr(self.instance, "name", "")
        slug = attrs.get("slug") or slugify(name)
        attrs["slug"] = slug

        slug_qs = Category.objects.filter(slug=slug)
        if self.instance:
            slug_qs = slug_qs.exclude(pk=self.instance.pk)
        if slug_qs.exists():
            raise serializers.ValidationError({
                "slug": "A category with this slug already exists. Use a different name or slug."
            })

        parent = attrs.get("parent", getattr(self.instance, "parent", None))
        if self.instance and parent and parent.pk == self.instance.pk:
            raise serializers.ValidationError({
                "parent": "A category cannot be its own parent."
            })
        return attrs
