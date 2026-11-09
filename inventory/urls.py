from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    LocationViewSet,
    ProductViewSet,
    ReceiptViewSet,
    StockMovementViewSet,
    SupplierViewSet,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("suppliers", SupplierViewSet, basename="supplier")
router.register("locations", LocationViewSet, basename="location")
router.register("products", ProductViewSet, basename="product")
router.register("movements", StockMovementViewSet, basename="movement")
router.register("receipts", ReceiptViewSet, basename="receipt")

urlpatterns = router.urls
