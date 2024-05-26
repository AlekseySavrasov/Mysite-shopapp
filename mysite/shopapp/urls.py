from django.urls import path, include
from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter

from .views import (
    ShopIndexView,
    GroupsListView,
    ProductDetailView,
    ProductListView,
    OrdersListView,
    OrderDetailView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
    OrderCreateView,
    OrderUpdateView,
    OrderDeleteView,
    ProductsDataExportView,
    OrdersDataExportView,
    ProductViewSet,
    OrderViewSet,
    LatestProductFeed,
    UserOrdersListView,
    UserOrdersListExportView,
)


app_name = "shopapp"

routers = DefaultRouter()
routers.register("products", ProductViewSet, basename="products")
routers.register("orders", OrderViewSet, basename="orders")

urlpatterns = [
    path("", ShopIndexView.as_view(), name="index"),
    path("api/", include(routers.urls)),
    path("groups/", GroupsListView.as_view(), name="groups_list"),
    path("products/", ProductListView.as_view(), name="products_list"),
    path("products/export/", ProductsDataExportView.as_view(), name="products-export"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/latest/feed/", LatestProductFeed(), name="products-feed"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product_details"),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),
    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("orders/export/", OrdersDataExportView.as_view(), name="orders-export"),
    path("orders/create/", OrderCreateView.as_view(), name="order_create"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_details"),
    path("orders/<int:pk>/update/", OrderUpdateView.as_view(), name="order_update"),
    path("orders/<int:pk>/delete/", OrderDeleteView.as_view(), name="order_delete"),
    path("users/<int:user_id>/orders/", UserOrdersListView.as_view(), name="user_orders_list"),
    path("users/<int:user_id>/orders/export/", UserOrdersListExportView.as_view(), name="user_orders-export"),
]
