import os
import pandas as pd
import logging

from app.store.storage import Storage
from app.store.scheme import Scheme
from app.store.custom_stotages.csv.filter_processor_csv import FilterProcessorCSV

log = logging.getLogger(__name__)

CVS_SEP = ';'

class StorageCVS(Storage):

    accessible_driver = ['cvs']

    def __init__(self, url ) -> None:

        super().__init__(url)

        self._is_opened        = False        
        self._opened_table_map = {}

    def _lazy_open(self, scheme: Scheme):

        scheme_cls = type(scheme)

        if( self._opened_table_map.get(scheme_cls) is not None ):
            return
        
        create_new_file = True
        filepath = os.path.join(self._dbname, scheme.table)
        file_exist = os.path.exists(filepath)

        if(file_exist):
            stats           = os.stat(filepath)
            create_new_file = (stats.st_size == 0)

        if( create_new_file ):
            store = pd.DataFrame([], columns=scheme.db_col_names())
        else:
            store = pd.read_csv(filepath, sep=CVS_SEP)
            
        self._opened_table_map[ scheme_cls ] = {
            'store': store, 
            'table_name':scheme.table,
            'db_col_names': scheme.db_col_names()
        }

    def _update_store_in_opened_table_map(
            self, 
            scheme : Scheme, 
            store : pd.DataFrame
        ):
        self._opened_table_map[ type(scheme) ]['store'] = store

    def _get_store_by_scheme(self, scheme : Scheme):
        return self._opened_table_map[ type(scheme) ]['store']
        
    async def close(self):
        for data in self._opened_table_map.values():
            del data['store']

        self._opened_table_map = {}

    async def count(self, scheme, filters):
        store = self._get_store_by_scheme(scheme)
        db_filter = self._build_db_query_filter(filters)
        return len(store.query(db_filter))

    async def flush(self):

        for scheme_cls, store_params in self._opened_table_map.items():
            filepath = os.path.join(self._dbname, store_params['table_name'])

            store_params['store'].to_csv(
                filepath, 
                sep=CVS_SEP, 
                columns=store_params['db_col_names'], 
                index=False
            )
   
    async def delete(self, scheme, filters, params :dict = None) -> None:

        self._lazy_open(scheme)
        db_query_filter = self._build_db_query_filter(filters)

        store = self._get_store_by_scheme(scheme)
        deleting_store = store.query(db_query_filter)
        store.drop(deleting_store.index.values, inplace=True)
        self._update_store_in_opened_table_map(scheme, store)

    async def drop_scheme(self, scheme, params : dict = None) -> None:
        pass
  
    async def install(self, schemes: list, params : dict = None) -> None:
        pass
        
    async def open(self, params : dict = None) -> bool:
      return True

    async def read(self, scheme, filters : dict, params : dict = None) -> list[dict]:

        self._lazy_open(scheme)

        store     = self._get_store_by_scheme(scheme)
        db_filter = self._build_db_query_filter(filters)
        df   = store.query(db_filter)
        df   = df.applymap(lambda x: None if pd.isna(x) else x)
        rows = df.to_dict(orient='records')
        
        return rows
    
    async def save(self, scheme : Scheme, db_record: dict, params : dict = None) -> None:
       
        self._lazy_open(scheme)
       
        primary_key = scheme.primary_key
        storage = self._get_store_by_scheme(scheme)
        primary_key_value   = db_record[ primary_key ]

        if(primary_key_value is None):
            db_record[ primary_key ] = scheme.new_primary_key()
            db_rows = []
        else:
            db_rows = self._read_rows_from_db(storage, scheme, db_record)
     
        store = self._update_db_record(storage, db_rows, db_record, primary_key )

        self._update_store_in_opened_table_map(scheme, store)
    
    def _read_rows_from_db(self, store : pd.DataFrame, scheme, db_record : dict):

        filters         = scheme.get_primary_key_values_pairs(db_record, True)
        db_query_filter = self._build_db_query_filter(filters)
        
        return store.query(db_query_filter)

    def _update_db_record(
            self, 
            store: pd.DataFrame, 
            db_rows : dict, 
            db_record : dict, 
            primary_key : str 
        ):

        if( len(db_rows) == 0 ):
            new_row_df = pd.DataFrame.from_dict([db_record])
            return pd.concat([store, new_row_df], ignore_index=True)
        else:
            idx = db_rows.index[0]

            if( db_record[primary_key ] is None ):
                db_record[primary_key ] = store.loc[idx, primary_key]
            
            store.loc[idx, db_record.keys() ] = list( db_record.values() )

            return store

    def _build_db_query_filter(self, filters):
        return FilterProcessorCSV().process(filters)
