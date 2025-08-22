import os
import shutil

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Loads all foundational data from fixture files. Run this for initial setup."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Starting database seeding process..."))

        # --- Copy Placeholder Images ---
        self.stdout.write(self.style.NOTICE("\nStep 1: Copying placeholder images..."))
        static_images = [
            'assets/images/placeholders/brand_placeholder.webp',
            'assets/images/placeholders/category_placeholder.webp',
            'assets/images/placeholders/product_placeholder.webp',
        ]

        for image_path in static_images:
            src_path = None
            for static_dir in settings.STATICFILES_DIRS:
                potential_src = os.path.join(static_dir, image_path)
                if os.path.exists(potential_src):
                    src_path = potential_src
                    break

            if not src_path:
                self.stderr.write(self.style.ERROR(f"  ✗ Static image not found: {image_path}"))
                continue

            filename = os.path.basename(image_path)
            dest_path = os.path.join(settings.MEDIA_ROOT, 'placeholders', filename)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            try:
                shutil.copy2(src_path, dest_path)
                self.stdout.write(self.style.SUCCESS(f"  ✓ Copied {image_path}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"  ✗ Failed to copy {image_path}: {e}"))

        # --- Load Fixtures ---
        self.stdout.write(self.style.NOTICE("\nStep 2: Loading data fixtures..."))

        fixtures = [
            'apps/core/fixtures/currencies.json',

            'apps/products/fixtures/brands.json',
            'apps/products/fixtures/categories.json',
            'apps/products/fixtures/tags.json',
            'apps/products/fixtures/attributes.json',
            'apps/products/fixtures/attribute_values.json',
            'apps/products/fixtures/product_types.json',
            'apps/products/fixtures/product_type_attributes.json',
            'apps/products/fixtures/products_and_variants.json',
            'apps/products/fixtures/product_collections.json',
            'apps/products/fixtures/back_in_stock.json'
        ]

        for fixture_path in fixtures:
            absolute_path = os.path.join(settings.BASE_DIR, fixture_path)

            if not os.path.exists(absolute_path):
                self.stderr.write(self.style.ERROR(f"  ✗ Fixture file not found: {absolute_path}"))
                continue

            self.stdout.write(self.style.NOTICE(f"  - Loading fixture: {fixture_path}"))
            try:
                call_command('loaddata', absolute_path)
                self.stdout.write(self.style.SUCCESS(f"    ✓ Successfully loaded {fixture_path}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"    ✗ Failed to load {fixture_path}: {e}"))

        self.stdout.write(self.style.SUCCESS("\n✓ Initial data loaded successfully!"))
