
from abc import ABC, abstractmethod

from app.store.scheme import Scheme
from app.store.factories.schemes_factory import SchemeFactory
from app.store.filters.filter import Filters
from app.store.sorting.sorting import Sorting
from app.store.paging.paging import Paging

class Datamapper(ABC):

    def __init__(self) -> None:

        self._storage     = None
        self._dataobjects = []

    async def __aenter__(self):
        await self._storage.open()
        return self

    async def __aexit__(self, *args):
       
        await self.write_dataobjects_to_db()
        await self._storage.close()
        
    def add_dataobject(self, dataobject) -> None:

        if dataobject not in self._dataobjects:
            self._dataobjects.append(dataobject)

    def reset_dataobjects(self) -> None:
        self._dataobjects = []

    @abstractmethod
    async def count(self, scheme, filters):
        pass

    
    async def install(self):

        scheme_factory = SchemeFactory()
        schemes = []

        for scheme in scheme_factory:
            schemes.append(scheme)

        await self._storage.install(schemes)

    @abstractmethod
    def init_storage():
        pass

    @abstractmethod
    async def delete_dataobjects_from_db(self):
        pass

    @abstractmethod
    async def fill_instance_from_db(self, cls_instance) -> None:
        pass

   
    @abstractmethod
    async def read(
        self, 
        filters: Filters = None, 
        sorting: Sorting = None, 
        paging: Paging = None
    ):
        pass

    @abstractmethod
    async def write_dataobjects_to_db(self) -> None:
        pass 

   


