from abc import ABC, abstractmethod


class BasePaymentGateway(ABC):
    """An abstract base class that defines the contract for all payment gateways."""

    def __init__(self, **config) -> None:
        self.config = config

    @abstractmethod
    def initiate_payment(self, order, request):
        """
        Initiates the payment process by connecting to the gateway.

        Returns:
            A tuple containing:
            - payment_url (str): The URL to redirect the user to.
            - gateway_token (str): A unique token from the gateway to track this request.
        """
        raise NotImplementedError("Each gateway must implement the 'initiate_payment' method.")

    @abstractmethod
    def verify_payment(self, request):
        """
        Verifies the payment after the user is redirected back from the gateway.

        Returns:
            A tuple containing:
            - is_successful (bool): True if the payment was successful.
            - gateway_transaction_id (str | None): The final transaction ID from the gateway.
            - gateway_response (dict): The full response from the gateway for logging.
        """
        raise NotImplementedError("Each gateway must implement the 'verify_payment' method.")

    @abstractmethod
    def parse_token(self, query_params):
        """Extracts the unique gateway token (e.g., authority, session_id) from the callback query parameters dictionary."""
        raise NotImplementedError
