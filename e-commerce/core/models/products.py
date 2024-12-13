from core.utils import TimeStampedModel
from django.db import models


class Category(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Category name")
    parent_category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Parent category",
        related_name="subcategories",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Product(TimeStampedModel):
    name = models.CharField(max_length=255, verbose_name="Product name")
    description = models.TextField(verbose_name="Product description")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Product price")
    stock_quantity = models.PositiveIntegerField(verbose_name="Stock quantity")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name="Product category"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"


class Review(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="reviews")
    comment = models.TextField(verbose_name="Review comment")
    rating = models.PositiveIntegerField(verbose_name="Rating")

    def __str__(self):
        return f"Review for {self.product.name} by {self.user.username}"

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        unique_together = ["product", "user"]
        indexes = [models.Index(fields=["product", "user"])]
