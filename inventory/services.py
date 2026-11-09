"""Business rules for stock movements."""

from django.db import transaction
from django.db.models import Sum

from .models import Location, Product, StockMovement


class MovementError(ValueError):
    """Raised when a stock movement breaks a rule."""


def stock_level(product: Product, location: Location | None = None) -> int:
    """Current stock of a product, in total or at one location."""
    movements = StockMovement.objects.filter(product=product)
    if location is not None:
        movements = movements.filter(location=location)
    return movements.aggregate(total=Sum("quantity_delta"))["total"] or 0


def validate_delta(movement_type: str, quantity_delta: int) -> None:
    if quantity_delta == 0:
        raise MovementError("quantity_delta must not be zero.")
    if movement_type == StockMovement.Type.IN and quantity_delta < 0:
        raise MovementError("Stock-in movements need a positive quantity_delta.")
    if movement_type == StockMovement.Type.OUT and quantity_delta > 0:
        raise MovementError("Stock-out movements need a negative quantity_delta.")


@transaction.atomic
def record_movement(
    *,
    product: Product,
    location: Location,
    movement_type: str,
    quantity_delta: int,
    note: str = "",
    user=None,
) -> StockMovement:
    """Record a movement, refusing anything that would make stock negative."""
    validate_delta(movement_type, quantity_delta)

    # Lock the product row so two simultaneous movements cannot both pass the check.
    locked_product = Product.objects.select_for_update().get(pk=product.pk)
    if not locked_product.is_active:
        raise MovementError("This product is inactive.")

    if stock_level(locked_product, location) + quantity_delta < 0:
        raise MovementError("Not enough stock at this location.")

    return StockMovement.objects.create(
        product=locked_product,
        location=location,
        movement_type=movement_type,
        quantity_delta=quantity_delta,
        note=note,
        created_by=user if getattr(user, "is_authenticated", False) else None,
    )
