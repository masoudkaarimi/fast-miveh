from django.core.management.base import BaseCommand
from django.db import transaction

from apps.configuration.factories import CurrencyFactory
from apps.configuration.models import Currency, SiteConfiguration
from apps.payments.models import PaymentGateway


class Command(BaseCommand):
    """
    Seeds the database with currencies and the default site configuration.
    """
    help = 'Seeds the database with initial data for the configuration application.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('--- Seeding Configuration Data ---'))

        # 1. Clean up old data
        self._cleanup_data()

        # 2. Create currencies
        currencies = self._create_currencies()
        payment_gateways = self._create_payment_gateways()

        # 3. Create the singleton SiteConfiguration instance
        if currencies:
            self._create_site_configuration(default_currency=currencies[0], default_payment_gateway=payment_gateways)
        else:
            self.stdout.write(self.style.WARNING("  No currencies created, skipping site configuration setup."))

        self.stdout.write(self.style.SUCCESS('Successfully seeded the configuration data.'))

    def _cleanup_data(self):
        """Deletes all existing data from the configuration models."""
        self.stdout.write("  Deleting old configuration data...")
        SiteConfiguration.objects.all().delete()
        Currency.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("  Old data deleted."))

    def _create_currencies(self) -> list[Currency]:
        """Creates a batch of currencies using the factory."""
        self.stdout.write("  Creating new currencies...")
        currencies = CurrencyFactory.create_batch(size=5)
        self.stdout.write(self.style.SUCCESS(f"  {len(currencies)} new currencies created."))
        return currencies

    def _create_payment_gateways(self) -> list[PaymentGateway]:
        """Creates a batch of payment_gateways using the factory."""
        self.stdout.write("  Creating new payment gateways...")
        payment_gateways = paymentGatewayFactory.create_batch(size=5)
        self.stdout.write(self.style.SUCCESS(f"  {len(payment_gateways)} new payment gateways created."))
        return payment_gateways

    def _create_site_configuration(self, default_currency: Currency, default_payment_gateway: PaymentGateway):
        """Creates or updates the singleton SiteConfiguration object."""
        self.stdout.write("  Creating/Updating site configuration...")

        # get_or_create for the singleton model
        config, created = SiteConfiguration.objects.get_or_create(
            pk=1,  # solo models always have a pk of 1
            defaults={
                'site_name': 'Fast Miveh',
                'default_currency': default_currency,
                'default_payment_gateway': default_payment_gateway,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS("  Site configuration created for the first time."))
        else:
            # If it already existed, just ensure it has a default currency
            if not config.default_currency:
                config.default_currency = default_currency
                config.save()
            if not config.default_payment_gateway:
                config.default_payment_gateway = default_payment_gateway
                config.save()
            self.stdout.write(self.style.SUCCESS("  Site configuration checked/updated."))
