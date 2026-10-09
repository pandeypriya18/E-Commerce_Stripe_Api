from django.contrib import admin
from products.models import Product,Category

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','owner','category','price','stock','created_at','updated_at']
    search_fields = ['name',]
    list_filter = ['category','is_active']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id','category_name','created_at','updated_at']
    search_fields = ['category_name',]

