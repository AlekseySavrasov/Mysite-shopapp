from django.contrib.auth.models import Group
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import ListCreateAPIView

from .serializers import GroupSerializer, OrderSerializer, ProductSerializer
from shopapp.models import Order, Product


@api_view()
def hello_world_view(request: Request) -> Response:
    return Response({"message": "Hello, World!"})


class GroupListView(ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class ProductListView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderListView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
