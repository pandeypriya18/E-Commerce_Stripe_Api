from decimal import Decimal
import json
import razorpay
import hmac, hashlib
from django.http import HttpResponse
from django.conf import settings
from django.db import transaction
from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from order.models import Order, OrderItem, Payment
from order.serializers import OrderSerializer
from products.models import Product
from django.views.decorators.csrf import csrf_exempt


class OrderError(Exception):

    def __init__(self, message, http_status=status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.http_status = http_status

def get_razorpay_client():
    return razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )


def restore_stock(order):

    for item in order.items.all():
        product = Product.objects.select_for_update().get(pk=item.product_id)
        product.stock += item.quantity
        product.save(update_fields=["stock"])

class PlaceOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.role != "customer":
            return Response(
                {"error": "Only customer can place order"},
                status=status.HTTP_403_FORBIDDEN,
            )

        items = request.data.get("items", [])  # [{"product_id": 1, "quantity": 2}]
        address = request.data.get("shipping_address")
        method = request.data.get("payment_method", Order.PaymentMethod.COD)

        if not items or not address:
            return Response(
                {"error": "items and shipping_address are required"}, status=400
            )
        if method not in Order.PaymentMethod.values:
            return Response(
                {"error": "payment_method must be 'cod' or 'online'"}, status=400
            )

        is_online = method == Order.PaymentMethod.ONLINE

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    customer=request.user,
                    shipping_address=address,
                    payment_method=method,
                    payment_status=Order.PaymentStatus.PENDING,
                    order_status=(
                        Order.OrderStatus.PENDING_PAYMENT
                        if is_online
                        else Order.OrderStatus.CONFIRMED
                    ),
                )
                total = Decimal("0")

                for item in items:
                    try:
                        qty = int(item.get("quantity", 0))
                        product_id = int(item["product_id"])
                    except (TypeError, ValueError, KeyError):
                        raise OrderError("Invalid item data")
                    if qty <= 0:
                        raise OrderError("Invalid quantity")

                    product = Product.objects.select_for_update().filter(id=product_id).first()
                    if not product:
                        raise OrderError("Product not found", status.HTTP_404_NOT_FOUND)
                    if product.owner == request.user:
                        raise OrderError("You can't buy your own product")
                    if product.stock < qty:
                        raise OrderError(f"Not enough stock for {product.name}")

                    product.stock -= qty
                    product.save(update_fields=["stock"])

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=qty,
                        price_at_purchase=product.price,
                    )
                    total += product.price * qty

                order.total_amount = total
                order.save(update_fields=["total_amount"])

                response = {
                    "order_id": order.id,
                    "total": total,
                    "payment_method": method,
                    "order_status": order.order_status,
                    "payment_status": order.payment_status,
                }

                if is_online:
                    amount_paise = int((total * 100).to_integral_value())
                    try:
                        rz_order = get_razorpay_client().order.create(
                            data={
                                "amount": amount_paise,
                                "currency": "INR",
                                "receipt": f"order_{order.id}", 
                                "notes": {"order_id": str(order.id)},
                            }
                        )
                    except Exception:
                        raise OrderError(
                            "Could not start payment. Please try again.",
                            status.HTTP_502_BAD_GATEWAY,
                        )

                    Payment.objects.create(
                        order=order,
                        razorpay_order_id=rz_order["id"],
                        amount=total,
                        currency=rz_order["currency"],
                    )
                    response.update(
                        {
                            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
                            "razorpay_order_id": rz_order["id"],
                            "amount": rz_order["amount"],  # paise
                            "currency": rz_order["currency"],
                        }
                    )
        except OrderError as e:
            return Response({"error": e.message}, status=e.http_status)

        return Response(response, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        order = Order.objects.filter(id=id, customer=request.user).first()
        if not order:
            return Response({"error": "Order not found"}, status=404)
        return Response(OrderSerializer(order).data)


class VerifyPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        rz_order_id = request.data.get("razorpay_order_id")
        rz_payment_id = request.data.get("razorpay_payment_id")
        signature = request.data.get("razorpay_signature")

        if not (rz_order_id and rz_payment_id and signature):
            return Response({"error": "All fields are required."}, status=400)

        payment = (
            Payment.objects.select_related("order")
            .filter(razorpay_order_id=rz_order_id, order__customer=request.user)
            .first()
        )
        if not payment:
            return Response({"error": "Payment record not found."}, status=404)

        if payment.status == Payment.Status.PAID:
            return Response({"message": "Payment already verified.", "order_id": payment.order_id})

        try:
            get_razorpay_client().utility.verify_payment_signature(
                {
                    "razorpay_order_id": rz_order_id,
                    "razorpay_payment_id": rz_payment_id,
                    "razorpay_signature": signature,
                }
            )
        except razorpay.errors.SignatureVerificationError:
            return Response({"error": "Payment verification failed."}, status=400)

        with transaction.atomic():
            payment.razorpay_payment_id = rz_payment_id
            payment.razorpay_signature = signature
            payment.status = Payment.Status.PAID
            payment.save()

            order = payment.order
            order.payment_status = Order.PaymentStatus.PAID
            order.order_status = Order.OrderStatus.CONFIRMED
            order.save(update_fields=["payment_status", "order_status", "updated_at"])

        return Response(
            {"message": "Payment verified successfully.", "order_id": order.id},
            status=status.HTTP_200_OK,
        )
    
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@csrf_exempt
def razorpay_webhook(request):
    body = request.body.decode("utf-8")
    signature = request.headers.get("X-Razorpay-Signature")

    secret = settings.RAZORPAY_WEBHOOK_SECRET
    print("Secret length:", len(secret), "| repr ends with:", repr(secret[-2:]))
    expected = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    print("Match:", hmac.compare_digest(expected, signature or ""))
    print("Event:", json.loads(body).get("event"))

    try:
        client.utility.verify_webhook_signature(
            body, signature, settings.RAZORPAY_WEBHOOK_SECRET
        )
   
    except Exception as e:
        print("Webhook error:", repr(e))
        print("Signature header:", signature)
        print("Secret loaded:", bool(settings.RAZORPAY_WEBHOOK_SECRET))
        return HttpResponse(status=400)

    data = json.loads(body)
    event = data["event"]

    if event == "payment.captured":
        rp_order_id = data["payload"]["payment"]["entity"]["order_id"]
        Payment.objects.filter(razorpay_order_id=rp_order_id).update(status="Paid")

    elif event == "payment.failed":
        rp_order_id = data["payload"]["payment"]["entity"]["order_id"]
        Payment.objects.filter(razorpay_order_id=rp_order_id).update(status="Failed")

    return HttpResponse(status=200)

def payment_page(request): 
    return render(request, "payment.html", {"razorpay_key_id": settings.RAZORPAY_KEY_ID})