from products.views import ProductView , CategoryView
from django.urls import path

urlpatterns = [
    path('products/', ProductView.as_view(), name = 'products'),
    path('products/<int:id>/', ProductView.as_view()),
    path('category', CategoryView.as_view(),name= "category"),
    path('category/<int:id>/',CategoryView.as_view()),
]

