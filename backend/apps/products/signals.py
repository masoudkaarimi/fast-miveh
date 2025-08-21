from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from apps.products.models import Product, ProductVariant


@receiver(post_save, sender=Product)
def sync_product_active_status_to_variants(sender, instance, **kwargs):
    """If a Product is made inactive, this signal ensures all its variants are also made inactive to maintain data integrity."""

    if instance.is_active is False:
        instance.variants.filter(is_active=True).update(is_active=False)


@receiver(post_save, sender=ProductVariant)
def manage_default_variant(sender, instance, created, **kwargs):
    """
    Ensures that there is always one and only one default variant for a product.
    - If a new variant is created and it's the only one, it becomes the default.
    - If a variant is explicitly set as default, any other default is unset.
    """
    product = instance.product

    if instance.is_default:
        product.variants.filter(is_default=True).exclude(pk=instance.pk).update(is_default=False)

    if not product.variants.filter(is_default=True).exists():
        first_variant = product.variants.filter(is_active=True).first()
        if first_variant:
            ProductVariant.objects.filter(pk=first_variant.pk).update(is_default=True)


@receiver(post_delete, sender=ProductVariant)
def reassign_default_variant_on_delete(sender, instance, **kwargs):
    """If the deleted variant was the default, assign a new default variant."""
    if not instance.is_default:
        return

    product = instance.product
    if not product.variants.filter(is_default=True).exists():
        new_default = product.variants.filter(is_active=True).first()
        if new_default:
            ProductVariant.objects.filter(pk=new_default.pk).update(is_default=True)


@receiver(m2m_changed, sender=ProductVariant.attributes.through)
def generate_variant_name_from_attributes(sender, instance, action, **kwargs):
    """Auto-generates the variant's name based on its attributes after they are added."""
    if action != "post_add":
        return

    if instance.name and instance.name != instance.sku:
        return

    attributes = instance.attributes.filter(attribute__is_active=True).order_by('attribute__name')
    if not attributes:
        return

    new_name = ", ".join(attr.value for attr in attributes)
    ProductVariant.objects.filter(pk=instance.pk).update(name=new_name)

# TODO: Cache Invalidation / Search Indexing Elasticsearch