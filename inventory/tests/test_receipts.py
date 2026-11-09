import pytest

from inventory.models import Product, Receipt, StockMovement, Supplier

pytestmark = pytest.mark.django_db


def post_receipt(client, lines, **extra):
    return client.post("/api/receipts/", {"lines": lines, **extra}, format="json")


def line(product, location, quantity, **extra):
    return {"product": product.id, "location": location.id, "quantity": quantity, **extra}


def stock_of(client, product):
    return client.get(f"/api/products/{product.id}/").json()["stock"]


def test_receiving_a_delivery_adds_stock_for_every_line(client, product, location, other_location):
    second = Product.objects.create(sku="SKU-002", name="Second item")

    response = post_receipt(
        client,
        [line(product, location, 10), line(second, other_location, 4)],
        reference="DN-1001",
    )

    assert response.status_code == 201
    assert response.json()["reference"] == "DN-1001"
    assert len(response.json()["movements"]) == 2
    assert stock_of(client, product) == 10
    assert stock_of(client, second) == 4


def test_every_line_becomes_a_stock_in_movement_on_one_receipt(client, product, location):
    post_receipt(client, [line(product, location, 5), line(product, location, 3)])

    receipt = Receipt.objects.get()
    movements = list(receipt.movements.all())
    assert len(movements) == 2
    assert {m.movement_type for m in movements} == {StockMovement.Type.IN}


def test_same_product_can_appear_on_several_lines(client, product, location):
    response = post_receipt(client, [line(product, location, 5), line(product, location, 3)])

    assert response.status_code == 201
    assert stock_of(client, product) == 8


def test_one_bad_line_rolls_back_the_whole_delivery(client, product, location):
    retired = Product.objects.create(sku="SKU-002", name="Retired", is_active=False)

    response = post_receipt(client, [line(product, location, 5), line(retired, location, 1)])

    assert response.status_code == 400
    assert "Line 2" in response.json()["detail"]
    assert Receipt.objects.count() == 0
    assert StockMovement.objects.count() == 0
    assert stock_of(client, product) == 0


def test_empty_delivery_is_rejected(client):
    response = post_receipt(client, [])

    assert response.status_code == 400
    assert "lines" in response.json()
    assert Receipt.objects.count() == 0


@pytest.mark.parametrize("quantity", [0, -3])
def test_quantity_must_be_positive(client, product, location, quantity):
    response = post_receipt(client, [line(product, location, quantity)])

    assert response.status_code == 400
    assert Receipt.objects.count() == 0


def test_unknown_product_is_rejected(client, location):
    response = client.post(
        "/api/receipts/",
        {"lines": [{"product": 999999, "location": location.id, "quantity": 1}]},
        format="json",
    )

    assert response.status_code == 400
    assert Receipt.objects.count() == 0


def test_supplier_is_recorded_and_receipts_can_be_filtered_by_it(client, product, location):
    acme = Supplier.objects.create(name="Acme")
    other = Supplier.objects.create(name="Other")
    post_receipt(client, [line(product, location, 1)], supplier=acme.id)
    post_receipt(client, [line(product, location, 1)], supplier=other.id)

    results = client.get(f"/api/receipts/?supplier={acme.id}").json()["results"]

    assert len(results) == 1
    assert results[0]["supplier"] == acme.id


def test_receipt_records_who_received_it(client, user, product, location):
    post_receipt(client, [line(product, location, 1)])

    assert Receipt.objects.get().created_by == user


def test_receipt_can_be_retrieved_with_its_movements(client, product, location):
    receipt_id = post_receipt(client, [line(product, location, 6, note="Fragile")]).json()["id"]

    data = client.get(f"/api/receipts/{receipt_id}/").json()

    assert len(data["movements"]) == 1
    assert data["movements"][0]["quantity_delta"] == 6
    assert data["movements"][0]["note"] == "Fragile"


def test_movements_link_back_to_their_receipt(client, product, location):
    receipt_id = post_receipt(client, [line(product, location, 2)]).json()["id"]

    results = client.get("/api/movements/").json()["results"]

    assert results[0]["receipt"] == receipt_id


def test_receipts_cannot_be_edited_or_deleted(client, product, location):
    receipt_id = post_receipt(client, [line(product, location, 2)]).json()["id"]

    assert client.patch(f"/api/receipts/{receipt_id}/", {"note": "x"}).status_code == 405
    assert client.delete(f"/api/receipts/{receipt_id}/").status_code == 405
    assert Receipt.objects.filter(pk=receipt_id).exists()


def test_receipts_require_authentication(anonymous_client):
    assert anonymous_client.get("/api/receipts/").status_code in (401, 403)
    assert anonymous_client.post("/api/receipts/", {}, format="json").status_code in (401, 403)
