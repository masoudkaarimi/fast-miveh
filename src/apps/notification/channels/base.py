from abc import ABC, abstractmethod


class BaseNotificationChannel(ABC):
    def __init__(self, **config: object) -> None:
        self.config: dict[str, object] = config

    @abstractmethod
    def send(self, recipient: str, **kwargs: object) -> None:
        """
        The main method to send a message.
        'recipient' is the target (e.g., email address, phone number, etc.).
        'kwargs' can contain message, subject, context, etc.
        """
        raise NotImplementedError("Each channel must implement the 'send' method.")
