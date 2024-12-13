from core.utils import TimeStampedModel
from django.db import models

from .products import Product


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = "new", "New"
        IN_PROGRESS = "in_progress", "In progress"
        DONE = "done", "Done"
        CANCELED = "canceled", "Canceled"

    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if self.pk:
            self.total_price = sum(item.price for item in self.items.all())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.pk} for {self.user.email}"

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user"])]


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        self.price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} ({self.quantity}) in order #{self.order.pk}"

    class Meta:
        indexes = [models.Index(fields=["order"]), models.Index(fields=["product"])]


class Payment(TimeStampedModel):
    class PaymentMethod(models.TextChoices):
        CARD = "card", "Card"
        CASH = "cash", "Cash"
        BANK = "bank", "Bank"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    payment_method = models.CharField(max_length=50, choices=PaymentMethod.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )

    def __str__(self):
        return f"Payment for order #{self.order.pk}"

    class Meta:
        indexes = [models.Index(fields=["order"])]
