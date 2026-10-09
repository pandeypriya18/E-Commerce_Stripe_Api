from django.contrib import admin
from order.models import Order , OrderItem , Payment

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','customer','payment_status','payment_method','total_amount','shipping_address']
    list_filter = ['payment_status',]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id','order','product','price_at_purchase','quantity']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['razorpay_order_id','razorpay_payment_id','razorpay_signature','order','amount']
    





