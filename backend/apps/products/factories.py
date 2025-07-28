from datetime import timezone

import factory
from faker import Faker
from factory.django import DjangoModelFactory

from apps.products.models import (
    Currency, Brand, Category, Tag, Attribute, AttributeValue,
    ProductType, ProductTypeAttribute, Product, ProductVariant, Price, Inventory, ProductCollection,
    ProductCollectionEntry
)

fake = Faker()


class CurrencyFactory(DjangoModelFactory):
    class Meta:
        model = Currency
        django_get_or_create = ('code',)

    code = factory.Iterator(['IRR', 'TOMAN', 'USD', 'EUR', 'GBP'])
    name = factory.LazyAttribute(lambda obj: {
        'IRR': 'Iranian Rial',
        'TOMAN': 'Iranian Toman',
        'USD': 'US Dollar',
        'EUR': 'Euro',
        'GBP': 'British Pound'
    }.get(obj.code, fake.currency_name()))
    symbol = factory.LazyAttribute(lambda obj: {
        'IRR': '﷼',
        'TOMAN': 'تومان',
        'USD': '$',
        'EUR': '€',
        'GBP': '£'
    }.get(obj.code, fake.currency_symbol()))
    exchange_rate = 1.0
    is_active = True
    is_default = False


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: f"{fake.word()}-{n}")
    slug = factory.LazyAttribute(lambda obj: fake.slug(obj.name))
    parent = None
    description = factory.Faker('sentence')
    image = None
    display_order = factory.Sequence(lambda n: n)
    is_active = True


class BrandFactory(DjangoModelFactory):
    class Meta:
        model = Brand
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: f"{fake.company()} {n}")
    slug = factory.LazyAttribute(lambda obj: fake.slug(obj.name))
    logo = None
    description = factory.Faker('sentence')
    display_order = factory.Sequence(lambda n: n)
    is_active = True


class TagFactory(DjangoModelFactory):
    class Meta:
        model = Tag
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: f"{fake.word()}-{n}")
    slug = factory.LazyAttribute(lambda obj: fake.slug(obj.name))
    is_active = True


class AttributeFactory(DjangoModelFactory):
    class Meta:
        model = Attribute
        django_get_or_create = ('name',)

    @factory.lazy_attribute
    def name(self):
        return fake.random_element(['Color', 'Size', 'Weight'])

    @factory.lazy_attribute
    def attribute_type(self):
        mapping = {
            'Color': Attribute.AttributeTypeChoices.TEXT,
            'Size': Attribute.AttributeTypeChoices.NUMBER,
            'Weight': Attribute.AttributeTypeChoices.NUMBER,
        }
        return mapping.get(str(self.name), Attribute.AttributeTypeChoices.TEXT)

    @factory.lazy_attribute
    def display_type(self):
        mapping = {
            'Color': Attribute.DisplayTypeChoices.COLOR_SWATCH,
            'Size': Attribute.DisplayTypeChoices.RADIO_BUTTON,
            'Weight': Attribute.DisplayTypeChoices.TEXT_INPUT,
        }
        return mapping.get(str(self.name), self.name)

    slug = factory.LazyAttribute(lambda obj: fake.slug(obj.name))
    unit = factory.Faker('word')
    help_text = factory.Faker('sentence')
    is_variant_defining = factory.Faker('pybool')
    is_filterable = factory.Faker('pybool')
    is_active = True


class AttributeValueFactory(DjangoModelFactory):
    class Meta:
        model = AttributeValue
        django_get_or_create = ('attribute', 'value')

    @factory.lazy_attribute
    def meta(self):
        if self.attribute.display_type == Attribute.DisplayTypeChoices.COLOR_SWATCH:
            return {"hex_code": fake.hex_color()}
        return None

    attribute = factory.SubFactory(AttributeFactory)
    value = factory.Sequence(lambda n: f"{fake.word().capitalize()}_{n}")
    slug = factory.LazyAttribute(lambda obj: fake.slug(obj.value))
    display_order = factory.Sequence(lambda n: n)


class ProductTypeFactory(DjangoModelFactory):
    class Meta:
        model = ProductType
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: f"{fake.bs()} {n}")
    slug = factory.LazyAttribute(lambda obj: fake.slug(obj.name))
    description = factory.Faker('sentence')
    display_order = factory.Sequence(lambda n: n)

    @factory.post_generation
    def attributes(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for attr in extracted:
                self.attributes.add(attr)
        else:
            self.attributes.add(*AttributeFactory.create_batch(3))


class ProductTypeAttributeFactory(DjangoModelFactory):
    class Meta:
        model = ProductTypeAttribute
        django_get_or_create = ('product_type', 'attribute')

    product_type = factory.SubFactory(ProductTypeFactory)
    attribute = factory.SubFactory(AttributeFactory)
    is_required = factory.Faker('pybool')
    display_order = factory.Sequence(lambda n: n)


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"{fake.catch_phrase()} {n}")
    slug = factory.LazyAttribute(lambda obj: fake.slug(obj.name))
    product_type = factory.SubFactory(ProductTypeFactory)
    brand = factory.SubFactory(BrandFactory)
    short_description = factory.Faker('sentence', nb_words=10)
    description = factory.Faker('paragraph')
    is_active = True
    published_at = factory.Faker('date_time_this_year', tzinfo=timezone.utc)

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for category in extracted:
                self.categories.add(category)
        else:
            for _ in range(fake.random_int(min=1, max=3)):
                self.categories.add(CategoryFactory())

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for tag in extracted:
                self.tags.add(tag)
        else:
            for _ in range(fake.random_int(min=0, max=2)):
                self.tags.add(TagFactory())


class ProductVariantFactory(DjangoModelFactory):
    class Meta:
        model = ProductVariant
        django_get_or_create = ('product', 'name')

    class Params:
        currency_obj = None
        create_price_and_inventory = True

    product = factory.SubFactory(ProductFactory)
    name = factory.Faker('word')
    sku = factory.Faker('ean8')
    upc = factory.Faker('ean13')
    is_default = factory.Faker('pybool')
    is_active = True

    @factory.post_generation
    def attributes(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for attr in extracted:
                self.attributes.add(attr)
        else:
            self.attributes.add(*AttributeValueFactory.create_batch(3))

    @factory.post_generation
    def price_and_inventory(self, create, extracted, *, currency_obj=None, create_price_and_inventory=True):
        if not create or not create_price_and_inventory:
            return

        if not currency_obj:
            currency_obj, _ = Currency.objects.get_or_create(code="TOMAN", defaults={'name': 'Iranian Toman', 'symbol': 'تومان'})

        PriceFactory.create(variant=self, currency=currency_obj)
        InventoryFactory.create(variant=self)


class ProductCollectionFactory(DjangoModelFactory):
    class Meta:
        model = ProductCollection
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: f"{fake.word().capitalize()} Collection {n}")
    slug = factory.LazyAttribute(lambda obj: fake.slug(obj.name))
    description = factory.Faker('sentence')
    image = None
    start_date = None
    end_date = None
    display_order = factory.Sequence(lambda n: n)
    is_active = factory.Faker('pybool')

    @factory.post_generation
    def products(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for product in extracted:
                self.products.add(product)
        else:
            self.products.add(*ProductFactory.create_batch(5))


class ProductCollectionEntryFactory(DjangoModelFactory):
    class Meta:
        model = ProductCollectionEntry
        django_get_or_create = ('collection', 'product')

    collection = factory.SubFactory(ProductCollectionFactory)
    product = factory.SubFactory(ProductFactory)
    display_order = factory.Sequence(lambda n: n)


class PriceFactory(DjangoModelFactory):
    class Meta:
        model = Price
        django_get_or_create = ('variant', 'currency')

    variant = factory.SubFactory(ProductVariantFactory, create_price_and_inventory=False)
    currency = factory.SubFactory(CurrencyFactory)
    base_price = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True, min_value=10000)
    sale_price = None
    sale_start_date = None
    sale_end_date = None
    cost_price = None


class InventoryFactory(DjangoModelFactory):
    class Meta:
        model = Inventory

    variant = factory.SubFactory(ProductVariantFactory, create_price_and_inventory=False)
    quantity = factory.Faker('random_int', min=0, max=100)
    reserved_quantity = factory.Faker('random_int', min=0, max=10)
    threshold = 10
    track_inventory = True
    allow_backorders = False
