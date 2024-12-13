from core.models.orders import Order, OrderItem
from core.models.shopping import CartItem, ShoppingCart, Wishlist, WishlistItem
from drf_spectacular.views import OpenApiParameter, extend_schema
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@extend_schema(tags=["shopping"])
class ShoppingCartViewSet(viewsets.GenericViewSet):
    class ShoppingCartSerializer(serializers.ModelSerializer):
        class CartItemSerializer(serializers.ModelSerializer):
            class Meta:
                model = CartItem
                fields = "__all__"
                ref_name = "CartItemSerializer"

        items = CartItemSerializer(many=True)

        class Meta:
            model = ShoppingCart
            fields = "__all__"
            ref_name = "ShoppingCartOutputSerializer"

    class RequestSerializer(serializers.Serializer):
        product_id = serializers.IntegerField()
        quantity = serializers.IntegerField(default=1)

        class Meta:
            ref_name = "ShoppingCartRequestSerializer"

    class MakeOrderSerializer(serializers.Serializer):
        items = serializers.ListField(
            child=serializers.IntegerField(), required=False, default=list
        )

        class Meta:
            ref_name = "ShoppingCartMakeOrderSerializer"

    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated,)
    queryset = ShoppingCart.objects.all()

    @extend_schema(
        summary="Make order", responses={status.HTTP_201_CREATED: None}, request=MakeOrderSerializer
    )
    @action(methods=["POST"], detail=False)
    def make_order(self, request):
        serializer = self.MakeOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = self.queryset.get(user=request.user)
        if not serializer.validated_data["items"]:
            cart_items = cart.items.all()
        else:
            cart_items = cart.items.filter(id__in=serializer.validated_data["items"])

        if not cart_items.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user)
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order, product=cart_item.product, quantity=cart_item.quantity
            )
            cart_item.delete()
        order.save()
        return Response(data={"order_id": order.id}, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Get shopping cart", responses=ShoppingCartSerializer)
    @action(methods=["GET"], detail=False)
    def get_shopping_cart(self, request):
        cart, _ = self.queryset.get_or_create(user=request.user)
        serializer = self.ShoppingCartSerializer(cart)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Add products to shopping cart",
        responses={status.HTTP_204_NO_CONTENT: None},
        request=RequestSerializer,
    )
    @action(methods=["POST"], detail=False)
    def add_product(self, request):
        serializer = self.RequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart, _ = self.queryset.get_or_create(user=request.user)
        cart_item, created_item = CartItem.objects.get_or_create(
            product_id=serializer.validated_data["product_id"], cart=cart
        )
        if created_item:
            cart_item.quantity = serializer.validated_data["quantity"]
        else:
            cart_item.quantity += serializer.validated_data["quantity"]
        cart_item.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Remove products from shopping cart",
        responses={status.HTTP_204_NO_CONTENT: None},
        parameters=[
            OpenApiParameter(name="quantity", type=int, required=False),
            OpenApiParameter(name="product_id", type=int, required=True),
        ],
    )
    @action(methods=["DELETE"], detail=False)
    def delete_product(self, request):
        serializer = self.RequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        cart, _ = self.queryset.get_or_create(user=request.user)
        try:
            cart_item = CartItem.objects.get(
                product_id=serializer.validated_data["product_id"], cart=cart
            )
            if cart_item.quantity > serializer.validated_data["quantity"]:
                cart_item.quantity -= serializer.validated_data["quantity"]
                cart_item.save()
            else:
                cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(summary="Clear shopping cart", responses={status.HTTP_204_NO_CONTENT: None})
    @action(methods=["DELETE"], detail=False)
    def clear_shopping_cart(self, request):
        cart = self.queryset.get(user=request.user)
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["wishlist"])
class WishlistViewSet(viewsets.GenericViewSet):
    class RequestSerializer(serializers.Serializer):
        product_id = serializers.IntegerField()

        class Meta:
            ref_name = "WishlistRequestSerializer"

    class WishlistSerializer(serializers.ModelSerializer):
        class WishlistItemSerializer(serializers.ModelSerializer):
            class Meta:
                model = WishlistItem
                fields = "__all__"
                ref_name = "WishlistItemSerializer"

        items = WishlistItemSerializer(many=True)

        class Meta:
            model = Wishlist
            fields = "__all__"
            ref_name = "WishlistOutputSerializer"

    permission_classes = [IsAuthenticated]
    serializer_class = WishlistSerializer
    queryset = Wishlist.objects.all()

    @extend_schema(summary="Get wishlist", responses=WishlistSerializer)
    @action(methods=["GET"], detail=False)
    def get_wishlist(self, request):
        wishlist, _ = self.queryset.get_or_create(user=request.user)
        serializer = self.serializer_class(wishlist)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="Clear wishlist", responses={status.HTTP_204_NO_CONTENT: None})
    @action(methods=["DELETE"], detail=False)
    def clear_wishlist(self, request):
        wishlist = self.queryset.get(user=request.user)
        wishlist.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Add product to wishlist",
        responses={status.HTTP_200_OK: None, status.HTTP_201_CREATED: None},
        request=RequestSerializer,
    )
    @action(methods=["POST"], detail=False)
    def add_product(self, request):
        serializer = self.RequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        wishlist, _ = self.queryset.get_or_create(user=request.user)
        _, created_item = WishlistItem.objects.get_or_create(
            product_id=serializer.validated_data["product_id"], wishlist=wishlist
        )
        return Response(status=status.HTTP_201_CREATED if created_item else status.HTTP_200_OK)

    @extend_schema(
        summary="Remove product from wishlist",
        responses={status.HTTP_204_NO_CONTENT: None},
        parameters=[
            OpenApiParameter(name="product_id", type=int, required=True),
        ],
    )
    @action(methods=["DELETE"], detail=False)
    def delete_product(self, request):
        serializer = self.RequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        wishlist, _ = self.queryset.get_or_create(user=request.user)
        try:
            wishlist_item = WishlistItem.objects.get(
                product_id=serializer.validated_data["product_id"], wishlist=wishlist
            )
            wishlist_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except WishlistItem.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)
