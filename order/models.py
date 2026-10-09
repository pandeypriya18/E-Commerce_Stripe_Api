from django.conf import settings
from django.db import models


class Order(models.Model):
    class PaymentMethod(models.TextChoices):
        COD = "cod", "Cash on Delivery"
        ONLINE = "online", "Online Payment"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    class OrderStatus(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "Pending Payment"
        CONFIRMED = "confirmed", "Confirmed"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    shipping_address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_method = models.CharField(
        max_length=10, choices=PaymentMethod.choices, default=PaymentMethod.COD
    )
    payment_status = models.CharField(
        max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    order_status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.CONFIRMED
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)


class Payment(models.Model):

    class Status(models.TextChoices):
        CREATED = "created", "Created"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    razorpay_order_id = models.CharField(max_length=100, unique=True )
    razorpay_payment_id = models.CharField(max_length=100)
    razorpay_signature = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.CREATED)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.razorpay_order_id} ({self.status})"