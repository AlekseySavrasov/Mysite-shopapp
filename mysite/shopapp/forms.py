from django import forms
from django.forms import ModelForm, ImageField, ClearableFileInput
from django.contrib.auth.models import Group

from .models import Product, Order


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ["name"]


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount", "preview"

    images = ImageField(
        widget=ClearableFileInput(attrs={"multiple": True})
    )


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = "user", "delivery_address", "promo_code", "products"


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()
