from core.models.orders import Order, OrderItem, Payment
from core.tasks import send_order_changed_notification
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@extend_schema(tags=["orders"])
class OrderViewSet(viewsets.GenericViewSet):
    class OrderSerializer(serializers.ModelSerializer):
        class PaymentSerializer(serializers.ModelSerializer):
            class Meta:
                model = Payment
                fields = "__all__"
                ref_name = "OrderPaymentSerializer"

        class OrderItemSerializer(serializers.ModelSerializer):
            class Meta:
                model = OrderItem
                fields = "__all__"
                ref_name = "OrderItemSerializer"

        payments = PaymentSerializer(many=True)
        items = OrderItemSerializer(many=True)

        class Meta:
            model = Order
            fields = "__all__"
            ref_name = "OrderSerializer"

    queryset = Order.objects.select_related("user").prefetch_related("items", "payments")
    # queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "pk"

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @extend_schema(summary="Get order detail")
    @action(methods=["GET"], detail=False)
    def get_detail(self, request, pk):
        order = self.get_object()
        return Response(self.serializer_class(order).data)

    @extend_schema(summary="Get all orders")
    @action(methods=["GET"], detail=False)
    def get_all(self, request):
        orders = self.get_queryset()
        return Response(self.serializer_class(orders, many=True).data)

    @extend_schema(summary="Change order status")
    @action(methods=["POST"], detail=False)
    def change_status(self, request, pk):
        order = self.get_object()
        order.status = request.data["status"]
        order.save()

        send_order_changed_notification.delay(order.id, f"Order status changed to {order.status}")
        return Response(self.serializer_class(order).data)
