from django.urls import path
from .views import CategoryListCreateView, CategoryRetrieveUpdateDestroyView, BrandListCreateView, BrandRetrieveUpdateDestroyView

urlpatterns = [
    
    path("categories/",CategoryListCreateView.as_view(), name="category_list_create"),
    path("category/<slug:slug>/",CategoryRetrieveUpdateDestroyView.as_view(), name="category_detail"),
    path("brands/",BrandListCreateView.as_view(), name="brand_list_create"),
    path("brand/<slug:slug>/",BrandRetrieveUpdateDestroyView.as_view(), name="brand_detail")
]