
from app.store.datamapper_common import DatamapperCommon
from app.store.custom_stotages.csv.storage_csv import StorageCVS


class DatamapperManagerCSV(DatamapperCommon):

    def __init__(self) -> None:
        
        super().__init__()
       
    def init_storage(self, url):
        self._storage = StorageCVS(url)
    
   