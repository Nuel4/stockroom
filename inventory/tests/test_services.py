import pytest

from inventory.models import StockMovement
from inventory.services import MovementError, record_movement, stock_level

pytestmark = pytest.mark.django_db


def test_stock_level_is_the_sum_of_movements(product, location, other_location):
    record_movement(product=product, location=location, movement_type="in", quantity_delta=8)
    record_movement(product=product, location=other_location, movement_type="in", quantity_delta=2)

    assert stock_level(product) == 10
    assert stock_level(product, location) == 8
    assert stock_level(product, other_location) == 2


def test_stock_level_of_untouched_product_is_zero(product):
    assert stock_level(product) == 0


def test_failed_movement_leaves_no_trace(product, location):
    record_movement(product=product, location=location, movement_type="in", quantity_delta=2)

    with pytest.raises(MovementError):
        record_movement(product=product, location=location, movement_type="out", quantity_delta=-3)

    assert StockMovement.objects.count() == 1
    assert stock_level(product) == 2
