from core.models.products import Category, Product, Review
from core.utils import CachedLimitOffsetPagination
from drf_spectacular.views import extend_schema
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ["user"]


@extend_schema(tags=["products"], summary="List of categories")
class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CachedLimitOffsetPagination


@extend_schema(tags=["products"], summary="Category details")
class CategoryDetailView(RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


@extend_schema(tags=["products"], summary="List of products")
class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CachedLimitOffsetPagination


@extend_schema(tags=["products"], summary="Product details")
class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


@extend_schema(tags=["products"], summary="Product reviews")
class ProductReviewListView(ListAPIView):
    serializer_class = ReviewSerializer
    pagination_class = CachedLimitOffsetPagination

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["pk"])


class ReviewViewSet(GenericViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    lookup_field = "pk"
    permission_classes = (IsAuthenticated,)

    @extend_schema(tags=["products"], summary="Add review to product")
    @action(methods=["POST"], detail=True)
    def add_review(self, request):
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["user"] = request.user
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(tags=["products"], summary="Delete review")
    @action(methods=["DELETE"], detail=True)
    def delete_review(self, request, pk):
        review = self.get_object()
        if review.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(tags=["products"], summary="Update review")
    @action(methods=["PUT"], detail=True)
    def update_review(self, request, pk):
        review = self.get_object()
        if review.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = ReviewSerializer(review, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(tags=["products"], summary="Review details")
    @action(methods=["GET"], detail=True)
    def get_review(self, request, pk):
        review = self.get_object()
        serializer = ReviewSerializer(review)
        return Response(serializer.data)
