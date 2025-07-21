from django.utils.translation import gettext_lazy as _


class ProductException(Exception):
    """Base exception for all product-related errors."""
    default_message = _("An error occurred in the products application.")

    def __init__(self, message=None):
        if message is None:
            message = self.default_message
        super().__init__(message)


class ProductNotFound(ProductException):
    """Raised when a product or variant is not found."""
    default_message = _("The requested product or variant does not exist.")


class InventoryError(ProductException):
    """Base exception for inventory-related issues."""
    default_message = _("An inventory-related error occurred.")


class OutOfStockError(InventoryError):
    """Raised when an operation is attempted on an out-of-stock item."""
    default_message = _("This item is currently out of stock.")


class InvalidAttributeCombination(ProductException):
    """Raised when a selected combination of attributes does not map to a valid variant."""
    default_message = _("The selected options do not form a valid product combination.")
