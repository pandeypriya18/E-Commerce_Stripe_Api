from django.urls import path
from order.views import (
    PlaceOrderView,
    OrderDetailView,
    VerifyPaymentView,
    razorpay_webhook,
    payment_page,
)

urlpatterns = [
    path("orders/place/", PlaceOrderView.as_view()),
    path("orders/<int:id>/", OrderDetailView.as_view()),
    path("payments/verify/", VerifyPaymentView.as_view()),
    path('payments/webhook/',razorpay_webhook),
    path("payments/payment/", payment_page),  # test page
]
