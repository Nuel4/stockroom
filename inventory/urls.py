from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    LocationViewSet,
    ProductViewSet,
    StockMovementViewSet,
    SupplierViewSet,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("suppliers", SupplierViewSet, basename="supplier")
router.register("locations", LocationViewSet, basename="location")
router.register("products", ProductViewSet, basename="product")
router.register("movements", StockMovementViewSet, basename="movement")

urlpatterns = router.urls
