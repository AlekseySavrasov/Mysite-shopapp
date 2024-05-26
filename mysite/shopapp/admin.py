from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from .admin_mixins import ExportAsCSVMixin
from .common import save_csv_products, save_csv_orders
from .models import Product, Order, ProductImage
from .forms import CSVImportForm


class CSVImportMixin:
    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form
            }
            return render(request, "admin/csv_form.html", context)

        form = CSVImportForm(request.POST, request.FILES)

        if not form.is_valid():
            context = {
                "form": form
            }
            return render(request, "admin/csv_form.html", context, status=400)

        self.save_csv_data(form, request)

        self.message_user(request, "Data from CSV was imported")
        return redirect("..")

    def save_csv_data(self, form, request):
        raise NotImplementedError("Subclasses should implement this method")


@admin.action(description="Archived products")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description="Unarchived products")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


class ProductInline(admin.TabularInline):
    model = Order.products.through


class OrderInline(admin.TabularInline):
    model = Product.orders.through


class ProductInline2(admin.StackedInline):
    model = ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin, CSVImportMixin):
    change_list_template = "shopapp/products_changelist.html"

    actions = [
        mark_archived,
        mark_unarchived,
        "export_csv",
    ]
    inlines = [
        OrderInline,
        ProductInline2,
    ]
    list_display = "pk", "name", "description_short", "discount", "price", "archived"
    list_display_links = "pk", "name"
    ordering = "pk",
    search_fields = "name", "description", "discount", "price"
    fieldsets = [
        (None, {
            "fields": ("name", "description")
        }),
        ("Price options", {
            "fields": ("price", "discount"),
            "classes": ("wide",)
        }),
        ("Images", {
            "fields": ("preview",)
        }),
        ("Extra options", {
            "fields": ("archived",),
            "classes": ("collapse",),
            "description": "Extra options. Field archived is for soft delete",
        })
    ]

    def description_short(self, an_object: Product) -> str:
        if len(an_object.description) > 48:
            return f"{an_object.description[:48]}..."
        return an_object.description

    def save_csv_data(self, form, request):
        save_csv_products(
            file=form.files["csv_file"].file,
            encoding=request.encoding,
        )

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-products-csv/",
                self.import_csv,
                name="import_products_csv",
            )
        ]
        return new_urls + urls


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin, ExportAsCSVMixin, CSVImportMixin):
    change_list_template = "shopapp/orders_changelist.html"

    inlines = [
        ProductInline,
    ]
    list_display = "delivery_address", "promo_code", "created_at", "user_verbose"
    search_fields = "delivery_address", "promo_code", "created_at",

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

    def save_csv_data(self, form, request):
        save_csv_orders(
            file=form.files["csv_file"].file,
            encoding=request.encoding,
        )

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-orders-csv/",
                self.import_csv,
                name="import_orders_csv",
            )
        ]
        return new_urls + urls
