from rest_framework import serializers
from products.models import Product , Category
from rest_framework.validators import ValidationError

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['name','price','stock','category']

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['category_name','created_at','updated_at']

    def validate_category_name(self , value ):
        if Category.objects.filter(category_name=value).exists():
            raise ValidationError("Category name already exists.")
        return value
        

