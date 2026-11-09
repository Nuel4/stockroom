from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Location, Product, Receipt, StockMovement, Supplier
from .serializers import (
    CategorySerializer,
    LocationSerializer,
    ProductSerializer,
    ReceiptSerializer,
    StockMovementSerializer,
    SupplierSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ["name"]


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    search_fields = ["name"]


class LocationViewSet(viewsets.ModelViewSet):
    """Locations hold movement history, so they can be edited but not deleted."""

    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    search_fields = ["name"]
    http_method_names = ["get", "post", "put", "patch", "head", "options"]


class ProductViewSet(viewsets.ModelViewSet):
    """Products keep their history, so retire them with is_active=false instead of deleting."""

    serializer_class = ProductSerializer
    filterset_fields = ["category", "supplier", "is_active"]
    search_fields = ["sku", "name"]
    ordering_fields = ["name", "sku", "created_at"]
    http_method_names = ["get", "post", "put", "patch", "head", "options"]

    def get_queryset(self):
        return (
            Product.objects.select_related("category", "supplier")
            .annotate(stock=Coalesce(Sum("movements__quantity_delta"), 0))
            .order_by("name", "id")
        )

    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request):
        """Active products at or below their reorder level (reorder level 0 means no alert)."""
        queryset = self.filter_queryset(self.get_queryset()).filter(
            is_active=True, reorder_level__gt=0, stock__lte=F("reorder_level")
        )
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page is not None else queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="stock")
    def stock_by_location(self, request, pk=None):
        """Stock of one product, broken down by location."""
        product = self.get_object()
        rows = (
            StockMovement.objects.filter(product=product)
            .values("location_id", "location__name")
            .annotate(quantity=Sum("quantity_delta"))
            .order_by("location__name")
        )
        return Response(
            [
                {
                    "location": row["location_id"],
                    "location_name": row["location__name"],
                    "quantity": row["quantity"],
                }
                for row in rows
            ]
        )


class StockMovementViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Append-only: movements can be created and read, never edited or deleted."""

    queryset = StockMovement.objects.select_related("product", "location")
    serializer_class = StockMovementSerializer
    filterset_fields = ["product", "location", "movement_type"]
    ordering_fields = ["created_at"]


class ReceiptViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """A delivery with several lines, recorded all together or not at all."""

    queryset = Receipt.objects.select_related("supplier").prefetch_related("movements")
    serializer_class = ReceiptSerializer
    filterset_fields = ["supplier"]
    search_fields = ["reference"]
    ordering_fields = ["created_at"]
