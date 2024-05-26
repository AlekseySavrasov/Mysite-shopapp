from csv import DictReader
from io import TextIOWrapper

from shopapp.models import Product, Order


def save_csv_products(file, encoding):
    """Saves product data from a CSV file to the Product model."""
    with TextIOWrapper(file, encoding=encoding) as csv_file:
        reader = DictReader(csv_file)
        objects = [Product(**row) for row in reader]
        Product.objects.bulk_create(objects)
        return objects


def save_csv_orders(file, encoding):
    with TextIOWrapper(file, encoding=encoding) as csv_file:
        reader = DictReader(csv_file)
        for row in reader:

            order_data = {
                'delivery_address': row['delivery_address'],
                'promo_code': row['promo_code'],
                'created_at': row['created_at'],
                'user_id': row['user_id'],
            }
            order = Order.objects.create(**order_data)

            product_ids = row['product_ids'].split(',')
            products = Product.objects.filter(id__in=product_ids)
            order.products.set(products)
