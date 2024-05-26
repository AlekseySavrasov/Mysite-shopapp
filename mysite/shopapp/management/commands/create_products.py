from django.core.management import BaseCommand
from shopapp.models import Product


class Command(BaseCommand):
    """Create products"""

    def handle(self, *args, **options):
        self.stdout.write("Create products")

        products_names = [
            "Laptop",
            "Desktop",
            "Smartphone",
        ]

        for product in products_names:
            product, created = Product.objects.get_or_create(name=product)
            self.stdout.write(f"{product.name} has been created")

        self.stdout.write(self.style.SUCCESS("Products was created"))
