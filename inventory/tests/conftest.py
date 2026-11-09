import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from inventory.models import Location, Product


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(username="tester")


@pytest.fixture
def client(user):
    api_client = APIClient()
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def anonymous_client():
    return APIClient()


@pytest.fixture
def location(db):
    return Location.objects.create(name="Main shelf")


@pytest.fixture
def other_location(db):
    return Location.objects.create(name="Back room")


@pytest.fixture
def product(db):
    return Product.objects.create(sku="SKU-001", name="Sample widget", reorder_level=5)


def post_movement(client, product, location, movement_type, quantity_delta, **extra):
    return client.post(
        "/api/movements/",
        {
            "product": product.id,
            "location": location.id,
            "movement_type": movement_type,
            "quantity_delta": quantity_delta,
            **extra,
        },
        format="json",
    )
