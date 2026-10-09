from rest_framework import serializers
from order.models import Order , OrderItem , Payment

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['customer','total_amount','shipping_address']
        read_only_fields = ['created_at','updated_at']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'