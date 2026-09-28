from django.contrib import admin
from order.models import Order , OrderItem , Payment

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer','status','total_amount']
admin.site.register(OrderItem)
admin.site.register(Payment)

