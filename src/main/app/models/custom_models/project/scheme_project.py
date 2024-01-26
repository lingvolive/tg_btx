from app.store.scheme import Scheme
from app.store.filters.filter import Filters, ConditionTypeEQ

from sqlalchemy import Column, Unicode, Boolean, BigInteger
 

class SchemeProject(Scheme):

    def __init__(self, dbobject_type_id) -> None:
        super().__init__(dbobject_type_id)
      
    def prepare_describe(self):
        self._describe = {
            'name': 'Projects',
            'table' : 'projects',
            'primary_key':'id',
            'secondary_key':[],
            'db_rules':{ 'property_to_db_col_map':{
                                                    'id'     : 'id',
                                                    'name'   : 'name',
                                                    'deleted':'deleted'
                                                },

                          'nested_objects': [],

                          'key_map_for_nested_schemes': {},
                            'db_col_types':{
                                'id': Column(BigInteger, primary_key=True),
                                'name':Column(Unicode, nullable=True),
                                'deleted':Column(Boolean, nullable=True),
                            },
                        },
            
        }

    def extract_schema_from_instance(self, cls_instance, owner=None) -> dict:

        scheme_struct = self.extract_schema_from_instance_default(cls_instance)
        
        return scheme_struct

    def fill_instance(self, cls_instance, record:dict):
        
        self.fill_instance_default(cls_instance, record)

    def get_primary_key_values_pairs(self, db_record : dict, is_save: bool ) -> list :

        filters = Filters()
       
        filters.new_filter(
            ConditionTypeEQ(), 
            self.primary_key, 
            db_record[self.primary_key] 
        )
       
        return filters
    
    def new_primary_key(self):
        pass

