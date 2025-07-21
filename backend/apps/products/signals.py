# In apps/products/signals.py

from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from .models import ProductVariant, AttributeValue


@receiver(post_save, sender=ProductVariant)
def manage_default_variant(sender, instance: ProductVariant, created: bool, **kwargs):
    """
    Ensures that there is always one and only one default variant for a product.
    - If a new variant is created and it's the only one, it becomes the default.
    - If a variant is explicitly set as default, any other default is unset.
    """
    product = instance.product

    # If a variant is saved with is_default=True
    if instance.is_default:
        # Unset the is_default flag for all other variants of the same product.
        # .exclude(pk=instance.pk) ensures we don't unset the current one.
        product.variants.filter(is_default=True).exclude(pk=instance.pk).update(is_default=False)

    # After the update, check if ANY default variant exists for the product.
    # If not (e.g., the first variant was created with is_default=False, or a default was deleted),
    # make this one the default.
    if not product.variants.filter(is_default=True).exists():
        # Find the first available active variant to promote as default.
        first_variant = product.variants.filter(is_active=True).first()
        if first_variant:
            # Use .update() to avoid triggering this signal again in a loop.
            ProductVariant.objects.filter(pk=first_variant.pk).update(is_default=True)


@receiver(post_delete, sender=ProductVariant)
def reassign_default_on_delete(sender, instance: ProductVariant, **kwargs):
    """
    If the deleted variant was the default, assign a new default variant.
    """
    # If the deleted variant was not the default, do nothing.
    if not instance.is_default:
        return

    product = instance.product
    # Check if any other variants exist.
    if product.variants.exists():
        # Check if, after deletion, there is still a default variant.
        # This is a safeguard, as the post_save signal should handle most cases.
        if not product.variants.filter(is_default=True).exists():
            # Promote the first active variant to be the new default.
            new_default = product.variants.filter(is_active=True).first()
            if new_default:
                new_default.is_default = True
                new_default.save(update_fields=['is_default'])


@receiver(m2m_changed, sender=ProductVariant.attributes.through)
def generate_variant_name_from_attributes(sender, instance: ProductVariant, action: str, **kwargs):
    """
    Auto-generates the variant's name based on its attributes after they are added.
    This signal fires when the ManyToManyField 'attributes' is changed.
    """
    # We only want to act after new attributes have been added.
    if action != "post_add":
        return

    # If the name is already set manually, do not overwrite it.
    if instance.name and instance.name != instance.sku:
        return

    # Fetch all attribute values, ordered by their attribute's name for consistency.
    # e.g., "Blue, Large" instead of "Large, Blue"
    attributes = instance.attributes.all().order_by('attribute__name')

    if not attributes:
        return

    # Join the values to create a descriptive name.
    new_name = ", ".join(attr.value for attr in attributes)

    # Update the instance without triggering save signals again.
    ProductVariant.objects.filter(pk=instance.pk).update(name=new_name)
