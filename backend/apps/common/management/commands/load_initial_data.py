import os
import shutil

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Loads all foundational data from fixture files. Run this for initial setup."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Starting database seeding process..."))

        # --- Copy Placeholder Images (This part is correct and remains unchanged) ---
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

        # --- Load Fixtures in correct order ---
        self.stdout.write(self.style.NOTICE("\nStep 2: Loading data fixtures..."))

        fixtures = [
            'apps/configuration/fixtures/01_currencies.json',

            'apps/products/fixtures/01_categories.json',
            'apps/products/fixtures/02_tags.json',
            'apps/products/fixtures/03_attributes.json',
            'apps/products/fixtures/04_attribute_values.json',
            'apps/products/fixtures/05_product_types.json',
            'apps/products/fixtures/06_products_and_variants.json'
        ]

        for fixture_path in fixtures:
            # Create the absolute path to the fixture file
            absolute_path = os.path.join(settings.BASE_DIR, fixture_path)

            if not os.path.exists(absolute_path):
                self.stderr.write(self.style.ERROR(f"  ✗ Fixture file not found: {absolute_path}"))
                continue

            self.stdout.write(self.style.NOTICE(f"  - Loading fixture: {fixture_path}"))
            try:
                # Use the absolute path instead of the relative fixture name
                call_command('loaddata', absolute_path)
                self.stdout.write(self.style.SUCCESS(f"    ✓ Successfully loaded {fixture_path}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"    ✗ Failed to load {fixture_path}: {e}"))

        self.stdout.write(self.style.SUCCESS("\n✓ Initial data loaded successfully!"))
