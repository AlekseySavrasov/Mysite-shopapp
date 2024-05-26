"""
В этом модуле лежат различные наборы представлений.

Разные views интернет-магазина: по товарам, заказам и т.д.
"""

import logging
from csv import DictWriter
from timeit import default_timer

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group, User
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .common import save_csv_products, save_csv_orders
from .forms import ProductForm, OrderForm, GroupForm
from .models import Product, Order, ProductImage
from .serializers import ProductSerializer, OrderSerializer


logger = logging.getLogger(__name__)


@extend_schema(description="Product view CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product.

    Полный CRUD для сущностей товара.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    )
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]
    ordering_fields = [
        "name",
        "price",
        "discount",
    ]
    search_fields = [
        "name",
        "description",
    ]

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves **product**, returns 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by id not found"),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):

        response = HttpResponse(content_type='text/csv')
        filename = "products-export.csv"
        response['Content-Disposition'] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
            "created_by_id",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow(
                {field: getattr(product, field) for field in fields}
            )
        return response

    @action(methods=["post"], detail=False, parser_classes=[MultiPartParser,])
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @method_decorator(cache_page(60))
    def list(self, request, *args, **kwargs):
        # print("Hello products list")
        return super().list(request, *args, **kwargs)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = (
        DjangoFilterBackend,
        OrderingFilter,
        SearchFilter,
    )
    list_params = [
        "created_at",
        "delivery_address",
        "user"
    ]
    filterset_fields = list_params
    ordering_fields = list_params
    search_fields = list_params

    @action(methods=["post"], detail=False, parser_classes=[MultiPartParser, ])
    def upload_csv(self, request: Request):
        products = save_csv_orders(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class ShopIndexView(View):

    # @method_decorator(cache_page(60))
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 999),
            ('Smartphone', 999),
        ]
        context = {
            "timer_running": default_timer(),
            "products": products,
            "items": 5,
        }
        logger.debug("Products for shop index %s", products)
        logger.info("Rendering shop index")
        print("Shop index context", context)
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)

        if form.is_valid():
            form.save()

        return redirect(request.path)


class ProductDetailView(DetailView):
    template_name = "shopapp/products-detail.html"
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductListView(ListView):
    template_name = 'shopapp/products-list.html'
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(UserPassesTestMixin, CreateView):
    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    model = Product
    form_class = ProductForm
    success_url = reverse_lazy("shopapp:products_list")


class ProductUpdateView(UserPassesTestMixin, PermissionRequiredMixin, UpdateView):
    def test_func(self):
        return self.request.user.is_superuser or (
                self.permission_required and self.model.created_by
        )

    permission_required = "shopapp.change_product"
    model = Product
    form_class = ProductForm
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        response = super().form_valid(form)

        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image
            )
        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects.
        select_related("user").
        prefetch_related('products')
    )


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order",
    queryset = (
        Order.objects.
        select_related("user").
        prefetch_related('products')
    )


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy("shopapp:orders_list")


class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderForm
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk},
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:orders_list")


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)

        if products_data is None:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived,
                }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)
            # elem = products_data[0]
            # name = elem["name"]
            # print("name", name)
        return JsonResponse({"products": products_data})


class OrdersDataExportView(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by("pk").all()
        orders_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promo_code": order.promo_code,
                "user_id": order.user.pk,
                "products": [product.pk for product in order.products.all()],
            }
            for order in orders
        ]

        return JsonResponse({"orders": orders_data})


class LatestProductFeed(Feed):
    title = "Shop products (latest)"
    description = "Updates changes and addition shop products"
    link = reverse_lazy("shopapp:products-list")

    def items(self):
        return (
            Product.objects
            .filter(created_at__isnull=False)
            .order_by("-created_at")[:5]
        )

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:200]


class UserOrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "shopapp/user_orders_list.html"
    context_object_name = "orders"
    login_url = "myauth:login"

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        self.owner = get_object_or_404(User, pk=user_id)
        return Order.objects.filter(user=self.owner)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["owner"] = self.owner
        return context


class UserOrdersListExportView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        user_id = self.kwargs.get("user_id")
        self.owner = get_object_or_404(User, pk=user_id)
        cache_key = f"user_orders_data_export_{user_id}"
        user_orders_data = cache.get(cache_key)

        if user_orders_data is None:
            orders = Order.objects.order_by("pk").filter(user=self.owner)
            user_orders_data = [
                {
                    "pk": order.pk,
                    "delivery_address": order.delivery_address,
                    "products": [product.pk for product in order.products.all()],
                    "author": order.user.username,
                }
                for order in orders
            ]
            cache.set(cache_key, user_orders_data, 60)
        return JsonResponse({"user_orders": user_orders_data})
