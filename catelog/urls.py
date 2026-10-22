from django.urls import path
from .views import CategoryListCreateView, CategoryRetrieveUpdateDestroyView

urlpatterns = [
    
    path("categories/",CategoryListCreateView.as_view(), name="category_list_create"),
    path("category/<slug:slug>/",CategoryRetrieveUpdateDestroyView.as_view(), name="category_detail")
]