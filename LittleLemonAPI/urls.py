from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, MenuItemViewSet, CartViewSet, OrderViewSet, ManagerViewSet, DeliveryCrewViewSet, BookViewSet
from djoser.views import UserViewSet

router = DefaultRouter(trailing_slash=False)
router.register('category', CategoryViewSet, basename='category')
router.register('menu-items', MenuItemViewSet, basename='menu-items')
router.register('cart/menu-items', CartViewSet, basename='cart/menu-items')
router.register('orders', OrderViewSet, basename='orders')
router.register('groups/manager/users', ManagerViewSet, basename='groups/manager')
router.register('groups/delivery-crew/users', DeliveryCrewViewSet, basename='groups/delivery-crew')
router.register('users', UserViewSet, basename='users')
router.register('books', BookViewSet, basename='books')
#router.register('books', BookView, basename='books')
urlpatterns = router.urls