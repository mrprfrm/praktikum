from abc import ABC, abstractmethod

class BaseStore(ABC):
    @abstractmethod
    def get_value(self, key):
        raise NotImplementedError

    @abstractmethod
    def set_value(self, key, value):
        raise NotImplementedError
