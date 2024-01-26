from abc import ABC, abstractmethod
from app.store.sorting.sorting import Sorting

class SortingProcessor(ABC):

    def __init__(self, params: dict = None) -> None:
        pass

    @abstractmethod
    def process(self, sorting: Sorting):
        pass
        