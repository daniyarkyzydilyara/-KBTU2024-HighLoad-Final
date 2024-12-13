import time
from logging import getLogger

from celery import shared_task
from core.models.orders import Order

logger = getLogger(__name__)


@shared_task
def send_order_changed_notification(order_id: int, message="Order status changed"):
    logger.info(f"Order {order_id}: {message}")

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")
        return

    # logic to send notification to user
    time.sleep(4)

    logger.info(f"Notification sent for order {order_id}")
