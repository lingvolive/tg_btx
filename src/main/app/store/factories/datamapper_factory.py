from app.services.metaclass import SingletonByID
from abc import ABC, abstractmethod
from app.store.custom_stotages.csv.datamappers_csv import DatamapperManagerCSV
from app.store.custom_stotages.postgres.datamappers_postgres import DatamapperManagerPostgres
from app.store.factories.storage_config_factory import (
    DBConfig, 
    DBConfigCVS, 
    DBConfigPostgres, 
    DBConfigFactory
)

class DatamapperAbstract(ABC):

    @abstractmethod
    def create(self):
        pass
    
class DatamapperFactoryCSV(DatamapperAbstract):

    def __init__(self) -> None:
        super().__init__()

        self._datamapper_manager = None

    def create(self):

        if(self._datamapper_manager is None):
            
            self._datamapper_manager = DatamapperManagerCSV()

        return self._datamapper_manager

class DatamapperFactoryPostgres(DatamapperAbstract):

    def __init__(self) -> None:
        super().__init__()

        self._datamapper_manager = None

    def create(self):

        if(self._datamapper_manager is None):
            self._datamapper_manager = DatamapperManagerPostgres()

        return self._datamapper_manager


class DatamapperFactory():

    _instance = None

    def __init__(self, id: str = 'local', db_config: DBConfig = None ) -> None:

        if(db_config == None):
            db_config = DBConfigFactory(id = id).get()
       
        if type(db_config) not in (DBConfigCVS, DBConfigPostgres):
            raise ValueError(f'Unsupported DB access method: {db_config.access_method()}')

        self._config = db_config
   
    def get(self):

        if(self._instance == None):
            if( isinstance(self._config, DBConfigCVS) ):
                self._factory = DatamapperFactoryCSV()
            elif( isinstance(self._config, DBConfigPostgres) ):
                self._factory = DatamapperFactoryPostgres()

            self._instance = self._factory.create()

        return self._instance