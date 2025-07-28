import random

from django.db import transaction
from django.core.management.base import BaseCommand

from faker import Faker

from apps.products.models import (
    Currency, Brand, Category, Tag, Attribute, AttributeValue,
    ProductType, Product, ProductVariant, Price, Inventory, ProductCollection,
    ProductCollectionEntry
)
from apps.products.factories import (
    CurrencyFactory, BrandFactory, CategoryFactory, TagFactory,
    ProductTypeFactory, ProductFactory, ProductVariantFactory,
    ProductCollectionFactory
)

fake = Faker()


class Command(BaseCommand):
    help = 'Seeds the database with initial data for the entire products application.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")

        self._cleanup_old_data()

        # --- Seeding Process ---
        currencies = self._create_currencies()
        brands = self._create_brands()
        categories = self._create_categories()
        tags = self._create_tags()
        product_types = self._create_product_types()

        products = self._create_products_with_variants(
            brands=brands,
            categories=categories,
            tags=tags,
            product_types=product_types,
            currencies=currencies
        )

        self._create_collections(products)

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database.'))

    def _cleanup_old_data(self):
        """Deletes all existing data from the relevant models in the correct order."""
        self.stdout.write("  Deleting old data...")
        # Order matters due to foreign key constraints
        models_to_delete = [
            ProductCollectionEntry, ProductCollection, Price, Inventory,
            ProductVariant, Product, ProductType, AttributeValue, Attribute,
            Tag, Category, Brand, Currency
        ]
        for model in models_to_delete:
            model.objects.all().delete()
        self.stdout.write("  Old data deleted.")

    def _create_currencies(self):
        """Creates a set of predefined currencies."""
        self.stdout.write("  Creating currencies...")
        currencies = CurrencyFactory.create_batch(size=5)
        self.stdout.write("  Currencies created.")
        return list(currencies)

    def _create_brands(self):
        """Creates a batch of brands."""
        self.stdout.write("  Creating 10 brands...")
        brands = BrandFactory.create_batch(10)
        self.stdout.write("  Brands created.")
        return list(brands)

    def _create_categories(self):
        """Creates a flat list of categories."""
        self.stdout.write("  Creating 10 categories...")
        categories = CategoryFactory.create_batch(10)
        self.stdout.write("  Categories created.")
        return list(categories)

    def _create_tags(self):
        """Creates a batch of tags."""
        self.stdout.write("  Creating 10 tags...")
        tags = TagFactory.create_batch(10)
        self.stdout.write("  Tags created.")
        return list(tags)

    def _create_product_types(self):
        """Creates a few product types."""
        self.stdout.write("  Creating 5 product types...")
        product_types = ProductTypeFactory.create_batch(5)
        self.stdout.write("  Product types created.")
        return list(product_types)

    def _create_products_with_variants(self, brands, categories, tags, product_types, currencies):
        """Creates products and, for each product, a random number of variants."""
        self.stdout.write("  Creating 30 products with variants...")

        all_products = []
        if not all([brands, categories, product_types, currencies]):
            self.stdout.write(self.style.WARNING("  Missing brands, categories, types, or currencies. Cannot create products."))
            return all_products

        for _ in range(30):
            # Create a single product with random associations
            product = ProductFactory(
                brand=random.choice(brands),
                categories=random.sample(categories, k=random.randint(1, 3)),
                tags=random.sample(tags, k=random.randint(0, 2)),
                product_type=random.choice(product_types)
            )
            all_products.append(product)

            # For each product, create 1 to 5 variants
            num_variants = random.randint(1, 5)
            ProductVariantFactory.create_batch(
                size=num_variants,
                product=product,
                currency_obj=random.choice(currencies)
            )

        self.stdout.write("  Products and variants created.")
        return all_products

    def _create_collections(self, products):
        """Creates collections and populates them with random products."""
        self.stdout.write("  Creating 5 product collections...")

        if not products:
            self.stdout.write(self.style.WARNING("  No products to add to collections."))
            return

        for _ in range(5):
            ProductCollectionFactory(products=random.sample(products, k=min(len(products), 15)))
        self.stdout.write("  Collections created.")
