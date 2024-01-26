from abc import ABC, abstractmethod
from app.services.url_parser import UrlParser

from app.store.filters.filter import Filters
from app.store.sorting.sorting import Sorting
from app.store.paging.paging import Paging



class Storage(ABC):

    def __init__(self, url:str) -> None:
        super().__init__()

        self._url  = url
        parsed_url = UrlParser.parse_url(url)

        self._driver     = parsed_url['driver']
        self._username   = parsed_url['username']
        self._password   = parsed_url['password']
        self._host       = parsed_url['hostname']
        self._dbname     = parsed_url['dbname']
        self._port       = parsed_url['port']
        self._url_params = parsed_url['params']

        self._is_driver_type_suitable()
    
    async def __enter__(self):
        self.open()
        return self

    async def __exit__(self):
        self.save()
        self.close()
    
    def _is_driver_type_suitable(self):

        assert self._driver in self.accessible_driver, \
            f'Driver type "{self._driver}" is not supported by the class "{type(self).__name__}"'  

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    async def count(self, scheme, filters):
        pass
    
    @abstractmethod
    async def delete(self, scheme, filters, params :dict = None) -> None:
        pass

    @abstractmethod
    async def drop_scheme(self, scheme, params : dict = None) -> None:
        pass

    @abstractmethod
    async def flush(self) -> None:
        pass

    @abstractmethod
    async def install(self, schemes: list, params : dict = None) -> None:
        pass
    
    @abstractmethod
    async def open(self, params : dict = None) -> bool:
        pass

    @abstractmethod
    async def read(self, scheme, filters: Filters,
                    sorting: Sorting = None, paging: Paging = None,
                    params : dict = None
    ) -> list[dict]:
        pass

    @abstractmethod
    async def save(self, scheme, db_record: dict, params : dict = None) -> None:
        pass

    