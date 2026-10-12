from rest_framework import serializers
from products.models import Product , Category

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['name','price','stock','category']

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['category_name','created_at','updated_at']