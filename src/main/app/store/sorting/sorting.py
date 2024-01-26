


class Sorting():

    def __init__(self, fields = [], direction = 'asc') -> None:
        self._fields = {}
        self.set_sorting(fields, direction)
    
    def set_sorting(self, fields, direction = 'asc'):
        
        for field in fields:
            self._fields[field] = direction

    def get_sorting(self) -> dict:
        return self._fields
    
    def new_sorting(self, field: str, direction = 'asc'):
        self._fields[field] = direction
        