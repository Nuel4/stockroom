from rest_framework import serializers

from .models import Category, Location, Product, StockMovement, Supplier
from .services import MovementError, record_movement, stock_level, validate_delta


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ["id", "name", "notes"]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "name", "description"]


class ProductSerializer(serializers.ModelSerializer):
    stock = serializers.SerializerMethodField()
    low_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "sku",
            "name",
            "category",
            "supplier",
            "unit",
            "reorder_level",
            "is_active",
            "stock",
            "low_stock",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_stock(self, obj: Product) -> int:
        annotated = getattr(obj, "stock", None)
        return annotated if annotated is not None else stock_level(obj)

    def get_low_stock(self, obj: Product) -> bool:
        return obj.is_active and obj.reorder_level > 0 and self.get_stock(obj) <= obj.reorder_level


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = [
            "id",
            "product",
            "location",
            "movement_type",
            "quantity_delta",
            "note",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "created_at"]

    def validate(self, attrs: dict) -> dict:
        try:
            validate_delta(attrs["movement_type"], attrs["quantity_delta"])
        except MovementError as exc:
            raise serializers.ValidationError({"quantity_delta": str(exc)}) from exc
        return attrs

    def create(self, validated_data: dict) -> StockMovement:
        user = self.context["request"].user
        try:
            return record_movement(user=user, **validated_data)
        except MovementError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc
