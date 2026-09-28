from django.contrib import admin
from products.models import Product,Category

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['seller','price','stock','is_active','created_at','updated_at']
    search_fields = ['name',]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name','created_at','updated_at']
    search_fields = ['category_name',]

