import pytest

from inventory.models import Product

from .conftest import post_movement

pytestmark = pytest.mark.django_db


def test_api_requires_authentication(anonymous_client):
    assert anonymous_client.get("/api/products/").status_code in (401, 403)
    assert anonymous_client.post("/api/movements/", {}, format="json").status_code in (401, 403)


def test_create_product(client):
    response = client.post(
        "/api/products/",
        {"sku": "SKU-100", "name": "Notebook", "unit": "pcs", "reorder_level": 10},
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["stock"] == 0
    assert Product.objects.filter(sku="SKU-100").exists()


def test_sku_must_be_unique(client, product):
    response = client.post(
        "/api/products/", {"sku": product.sku, "name": "Duplicate"}, format="json"
    )

    assert response.status_code == 400


def test_products_cannot_be_deleted(client, product):
    assert client.delete(f"/api/products/{product.id}/").status_code == 405


def test_product_can_be_retired(client, product):
    response = client.patch(f"/api/products/{product.id}/", {"is_active": False}, format="json")

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_search_products(client, product):
    Product.objects.create(sku="SKU-002", name="Other thing")

    results = client.get("/api/products/?search=widget").json()["results"]

    assert [item["sku"] for item in results] == ["SKU-001"]


def test_low_stock_lists_only_products_at_or_below_reorder_level(client, product, location):
    well_stocked = Product.objects.create(sku="SKU-002", name="Plenty", reorder_level=5)
    no_alert = Product.objects.create(sku="SKU-003", name="No alert", reorder_level=0)
    retired = Product.objects.create(sku="SKU-004", name="Retired", reorder_level=5)
    post_movement(client, product, location, "in", 3)
    post_movement(client, well_stocked, location, "in", 20)
    post_movement(client, no_alert, location, "in", 1)
    retired.is_active = False
    retired.save()

    results = client.get("/api/products/low-stock/").json()["results"]

    assert [item["sku"] for item in results] == ["SKU-001"]
    assert results[0]["low_stock"] is True


def test_product_with_no_movements_and_a_reorder_level_is_low(client, product):
    results = client.get("/api/products/low-stock/").json()["results"]

    assert [item["sku"] for item in results] == ["SKU-001"]


def test_stock_by_location(client, product, location, other_location):
    post_movement(client, product, location, "in", 10)
    post_movement(client, product, other_location, "in", 4)
    post_movement(client, product, location, "out", -3)

    rows = client.get(f"/api/products/{product.id}/stock/").json()

    assert {row["location_name"]: row["quantity"] for row in rows} == {
        "Main shelf": 7,
        "Back room": 4,
    }


def test_locations_cannot_be_deleted(client, location):
    assert client.delete(f"/api/locations/{location.id}/").status_code == 405
