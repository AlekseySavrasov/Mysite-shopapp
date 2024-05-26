from django.core.management import BaseCommand

from shopapp.models import Order, Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        order = Order.objects.first()

        if not order:
            self.stdout.write("no products")
            return

        products = Product.objects.all()

        for product in products:
            order.products.add(product)

        order.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Products {order.products.all()} have been added to order {order} successfully"
            )
        )
