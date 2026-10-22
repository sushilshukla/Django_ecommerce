from rest_framework import generics
from .models import Category
from .serializers import CategorySerializer
from .permissions import IsAdminOrReadOnly

class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        qs = Category.objects.all().order_by("sort_order","name")
        if self.request.user.is_authenticated and (
            self.request.user.role == 'admin' or self.request.user.is_staff
        ):
            return qs
        
        return qs.filter(is_active=True)
    
    
class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"
    http_method_names = ["get", "put", "patch", "delete", "head", "options"]
    
    def get_queryset(self):
        qs = Category.objects.all()
        
        if self.request.user.is_authenticated and (
            self.request.user.role == "admin" or self.request.user.is_staff
            ):
            return qs
        
        return qs.filter(is_active=True)