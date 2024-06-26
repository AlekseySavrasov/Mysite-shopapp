from django.contrib.auth.models import Group
from rest_framework import serializers

from shopapp.models import Order, Product


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "pk", "name"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
