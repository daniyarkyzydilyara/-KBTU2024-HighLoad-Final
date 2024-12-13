import pytest
from core.models.orders import Order, OrderItem, Payment
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="password")


@pytest.fixture
def auth_client(user):
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.fixture
def order(user):
    return Order.objects.create(user=user, status="pending")


@pytest.fixture
def order_item(order):
    return OrderItem.objects.create(
        order=order, product_name="Test Product", quantity=1, price=100.00
    )


@pytest.fixture
def payment(order):
    return Payment.objects.create(
        order=order, amount=100.00, method="credit_card", status="success"
    )


@pytest.mark.django_db
def test_get_all_orders(auth_client, order, order_item, payment):
    response = auth_client.get("/orders/get_all/")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == order.id
    assert response.data[0]["status"] == "pending"
    assert len(response.data[0]["items"]) == 1
    assert len(response.data[0]["payments"]) == 1


@pytest.mark.django_db
def test_get_order_detail(auth_client, order, order_item, payment):
    response = auth_client.get(f"/orders/get_detail/{order.id}/")
    assert response.status_code == 200
    assert response.data["id"] == order.id
    assert response.data["status"] == "pending"
    assert len(response.data["items"]) == 1
    assert len(response.data["payments"]) == 1


@pytest.mark.django_db
def test_change_order_status(auth_client, order):
    new_status = "completed"
    response = auth_client.post(f"/orders/change_status/{order.id}/", {"status": new_status})
    assert response.status_code == 200
    assert response.data["status"] == new_status

    # Verify the order's status was updated in the database
    order.refresh_from_db()
    assert order.status == new_status

    # Verify the notification task was called (mock task in actual tests)
