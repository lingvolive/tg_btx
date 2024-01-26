from app.store.sorting.sorting import Sorting
from app.store.sorting.sorting_processor import SortingProcessor

class SortingProcessorSqlAlchemy(SortingProcessor):

    def __init__(self, params: dict = None) -> None:
      super().__init__()
      self._alchemy_model = params['model']

    def process(self, sorting: Sorting):
        order_by_clause = []
        for field, direction in sorting.get_sorting().items():
            column = getattr(self._alchemy_model, field)
            if direction.lower() == 'desc':
                column = column.desc()
            order_by_clause.append(column)
        return order_by_clause