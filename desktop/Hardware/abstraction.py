from abc import ABC, abstractmethod


class AbstractDriver(ABC):

    @abstractmethod
    def update(self, state: bool) -> None: ...
