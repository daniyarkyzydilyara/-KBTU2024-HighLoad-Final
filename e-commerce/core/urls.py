from django.urls import path

from .views.orders import OrderViewSet
from .views.products import (
    CategoryDetailView,
    CategoryListView,
    ProductDetailView,
    ProductListView,
    ProductReviewListView,
    ReviewViewSet,
)
from .views.shopping import ShoppingCartViewSet, WishlistViewSet

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("categories/<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
    path("products/<int:pk>/reviews/", ProductReviewListView.as_view(), name="product-reviews"),
    path(
        "shopping-cart/",
        ShoppingCartViewSet.as_view({"get": "get_shopping_cart", "delete": "clear_shopping_cart"}),
        name="shopping-cart",
    ),
    path(
        "shopping-cart/order/",
        ShoppingCartViewSet.as_view({"post": "make_order"}),
        name="shopping-cart-order",
    ),
    path(
        "shopping-cart/products/",
        ShoppingCartViewSet.as_view({"post": "add_product", "delete": "delete_product"}),
        name="shopping-cart-product",
    ),
    path(
        "wishlist/",
        WishlistViewSet.as_view({"get": "get_wishlist", "delete": "clear_wishlist"}),
        name="wishlist",
    ),
    path(
        "wishlist/products/",
        WishlistViewSet.as_view({"post": "add_product", "delete": "delete_product"}),
        name="wishlist-products",
    ),
    path("reviews/", ReviewViewSet.as_view({"post": "add_review"}), name="reviews"),
    path(
        "reviews/<int:pk>/",
        ReviewViewSet.as_view(
            {"delete": "delete_review", "put": "update_review", "get": "get_review"}
        ),
        name="review-detail",
    ),
    path("orders/", OrderViewSet.as_view({"get": "get_all"}), name="order-list"),
    path(
        "orders/<int:pk>/",
        OrderViewSet.as_view({"get": "get_detail", "post": "change_status"}),
        name="order-detail",
    ),
]
