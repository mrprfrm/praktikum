from abc import ABC, abstractmethod
from dataclasses import dataclass

from .state import State


@dataclass
class BasePipe(ABC):
    state: State
    pipe: None

    @abstractmethod
    def run(self):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        state,  = (yield)
        self.run()
