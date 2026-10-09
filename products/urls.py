from products.views import ProductView , CategoryView
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register("category",CategoryView , basename='category')

urlpatterns = [
    path('products/', ProductView.as_view(), name = 'products'),
    path('products/<int:id>/', ProductView.as_view()),
]

urlpatterns += router.urls