
from app.store.datamapper_common import DatamapperCommon
from app.store.custom_stotages.postgres.storage_postgres import StoragePostgres


class DatamapperManagerPostgres(DatamapperCommon):

    def __init__(self) -> None:
        
        super().__init__()
       
    def init_storage(self, url):
        self._storage = StoragePostgres(url)
    
   