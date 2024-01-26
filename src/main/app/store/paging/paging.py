
class Paging():

    def __init__(self, page = 1, page_size = 10) -> None:
        self._page      = page
        self._page_size = page_size

    @property
    def page(self):
        return self._page 
    
    @property
    def offset(self):
        return (self._page - 1) * self._page_size
    
    @property
    def page_size(self):
        return self._page_size
    

