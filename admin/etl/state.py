from dataclasses import dataclass

from .stores import BaseStore


@dataclass
class State:
    store: BaseStore

    def __getattr__(self, item):
        self.store.get_value(item)

    def __setattr__(self, key, value):
        self.store.set_value(key, value)
