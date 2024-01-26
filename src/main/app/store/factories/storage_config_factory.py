from abc import ABC, abstractmethod
from app.services.metaclass import SingletonByID
from app.config.config import Config
from app.services.url_parser import UrlParser

class DBConfig( ABC):

    def __init__(self, url : str) -> None:
        super().__init__()
        self._url = url

    def url(self):
        return self._url


class DBConfigCVS(DBConfig):

    def __init__(self, url : str) -> None:
        super().__init__(url)

class DBConfigPostgres(DBConfig):

    def __init__(self, url : str) -> None:
        super().__init__(url)


class DBConfigFactory(metaclass=SingletonByID):

    _instance = None

    def __init__(self, id: str = 'local', url : str = None ) -> None:

        assert url is not None, 'URL can\'t be empty'

        self._id  = id
        self._url = url

        parsed_url = UrlParser.parse_url(self._url)
        self._driver = parsed_url.get('driver')

        assert self._driver in ('cvs', 'postgresql+asyncpg', 'mssql+pymssql'), \
            f'Unsupported DB access driver {self._driver}'
        
    def get(self):

        if(self._instance == None):
            if(self._driver == 'cvs'):
                self._instance = DBConfigCVS(self._url)
            elif(self._driver in ['postgresql+asyncpg', 'mssql+pymssql']):
                self._instance = DBConfigPostgres(self._url)

        return self._instance


