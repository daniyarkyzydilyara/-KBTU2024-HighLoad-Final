from django.contrib.admin import site

from .models.orders import Order, OrderItem, Payment
from .models.products import Category, Product, Review
from .models.shopping import CartItem, ShoppingCart, Wishlist, WishlistItem

site.register(Category)
site.register(Product)
site.register(Review)

site.register(Order)
site.register(OrderItem)
site.register(Payment)

site.register(ShoppingCart)
site.register(CartItem)
site.register(Wishlist)
site.register(WishlistItem)
