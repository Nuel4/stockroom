from django.contrib import admin

from .models import Category, Location, Product, StockMovement, Supplier

admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Location)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["sku", "name", "category", "reorder_level", "is_active"]
    list_filter = ["is_active", "category"]
    search_fields = ["sku", "name"]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    """Read-only: movements are created through the API so stock rules always apply."""

    list_display = ["created_at", "product", "location", "movement_type", "quantity_delta"]
    list_filter = ["movement_type", "location"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
