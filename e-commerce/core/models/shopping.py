from core.utils import TimeStampedModel
from django.db import models

from .products import Product


class ShoppingCart(TimeStampedModel):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="shopping_cart")

    def __str__(self):
        return f"Shopping cart for {self.user.email}"


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} ({self.quantity}) in cart for {self.cart.user.email}"


class Wishlist(TimeStampedModel):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="wishlist")

    def __str__(self):
        return f"Wishlist for {self.user.email}"


class WishlistItem(TimeStampedModel):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.name} in wishlist for {self.wishlist.user.email}"
