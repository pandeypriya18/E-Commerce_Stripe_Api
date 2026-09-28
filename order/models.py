from django.db import models
from accounts.models import User
from products.models import Product

class Order(models.Model):
    customer = models.ForeignKey(User , on_delete=models.CASCADE)

    STATUS_CHOICES = (
        ("pending" , "Pending"),
        ("shipped" , "Shipped"),
        ("cancelled" , "Cancelled"),
        ("delivered" , "Delivered")
    )
    status = models.CharField(max_length=10 , choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10 , decimal_places=2 , default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE , related_name='items')
    product = models.ForeignKey(Product , on_delete= models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10 ,decimal_places=2)

class Payment(models.Model):
    order = models.ForeignKey(Order , on_delete= models.CASCADE)
    stripe_payment_intent_id = models.CharField(max_length=200 , unique=True)
    STATUS_CHOICES = (
    ("requires_payment_method", "Requires Payment Method"),
    ("requires_confirmation", "Requires Confirmation"),
    ("requires_action", "Requires Action"),
    ("processing", "Processing"),
    ("succeeded", "Succeeded"),
    ("canceled", "Canceled"),
    )
    status = models.CharField(max_length=30 , choices=STATUS_CHOICES)
    amount = models.DecimalField(max_digits=10 , decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

