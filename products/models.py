from django.db import models
from accounts.models import AbstractBaseUser, MyUser
from django.core.validators import MinValueValidator

class Category(models.Model):
    category_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
     verbose_name_plural = 'Categories'


    def __str__(self):
        return self.category_name

class Product(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(MyUser , on_delete=models.CASCADE , related_name='products')
    category = models.ForeignKey(Category , on_delete=models.CASCADE )
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10 , decimal_places=2 , validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/media/')  
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        return self.stock > 0
    










