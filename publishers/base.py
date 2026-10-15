from abc import ABC, abstractmethod

class BasePublisher(ABC):
    @abstractmethod
    def authenticate(self, credentials: dict) -> bool:
        pass

    @abstractmethod
    def publish(self, title: str, content: str, **kwargs) -> dict:
        """Trả về dict: {'success': bool, 'external_id': str, 'url': str, 'error': str}"""
        pass