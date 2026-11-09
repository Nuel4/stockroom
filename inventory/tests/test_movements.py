import pytest

from inventory.models import StockMovement

from .conftest import post_movement

pytestmark = pytest.mark.django_db


def test_stock_in_increases_stock(client, product, location):
    response = post_movement(client, product, location, "in", 10)

    assert response.status_code == 201
    assert client.get(f"/api/products/{product.id}/").json()["stock"] == 10


def test_stock_out_decreases_stock(client, product, location):
    post_movement(client, product, location, "in", 10)
    response = post_movement(client, product, location, "out", -4)

    assert response.status_code == 201
    assert client.get(f"/api/products/{product.id}/").json()["stock"] == 6


def test_cannot_take_out_more_than_is_in_stock(client, product, location):
    post_movement(client, product, location, "in", 3)
    response = post_movement(client, product, location, "out", -5)

    assert response.status_code == 400
    assert StockMovement.objects.count() == 1
    assert client.get(f"/api/products/{product.id}/").json()["stock"] == 3


def test_stock_is_checked_per_location(client, product, location, other_location):
    post_movement(client, product, location, "in", 10)
    response = post_movement(client, product, other_location, "out", -1)

    assert response.status_code == 400


def test_stock_in_must_be_positive(client, product, location):
    response = post_movement(client, product, location, "in", -2)

    assert response.status_code == 400


def test_stock_out_must_be_negative(client, product, location):
    post_movement(client, product, location, "in", 10)
    response = post_movement(client, product, location, "out", 2)

    assert response.status_code == 400


def test_zero_quantity_is_rejected(client, product, location):
    response = post_movement(client, product, location, "adjust", 0)

    assert response.status_code == 400


def test_adjustment_can_correct_stock_either_way(client, product, location):
    post_movement(client, product, location, "in", 10)

    assert post_movement(client, product, location, "adjust", -2).status_code == 201
    assert post_movement(client, product, location, "adjust", 5).status_code == 201
    assert client.get(f"/api/products/{product.id}/").json()["stock"] == 13


def test_inactive_product_cannot_move(client, product, location):
    product.is_active = False
    product.save()

    response = post_movement(client, product, location, "in", 1)

    assert response.status_code == 400


def test_movement_records_who_made_it(client, user, product, location):
    response = post_movement(client, product, location, "in", 1, note="First delivery")

    assert response.status_code == 201
    movement = StockMovement.objects.get()
    assert movement.created_by == user
    assert movement.note == "First delivery"


def test_movements_cannot_be_edited_or_deleted(client, product, location):
    movement_id = post_movement(client, product, location, "in", 5).json()["id"]

    assert client.patch(f"/api/movements/{movement_id}/", {"note": "x"}).status_code == 405
    assert client.delete(f"/api/movements/{movement_id}/").status_code == 405
    assert StockMovement.objects.filter(pk=movement_id).exists()


def test_movements_can_be_filtered_by_type(client, product, location):
    post_movement(client, product, location, "in", 5)
    post_movement(client, product, location, "out", -1)

    results = client.get("/api/movements/?movement_type=out").json()["results"]

    assert len(results) == 1
    assert results[0]["quantity_delta"] == -1
