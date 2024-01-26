import json
import uuid
from app.store.scheme import Scheme
from app.models.factories.enum_domain_objects import domainObjectTypes
from app.store.filters.filter import Filters, ConditionTypeEQ

from sqlalchemy import Column, Unicode, Integer, BigInteger, TEXT, String
 

class SchemeRole(Scheme):

    def __init__(self, dbobject_type_id) -> None:
        super().__init__(dbobject_type_id)
      
    def prepare_describe(self):
        self._describe = {
            'name': 'roles',
            'table' : 'roles',
            'primary_key':'id',
            'secondary_key':['user_id'],
            'db_rules':{ 'property_to_db_col_map':{
                                                    'id'     : 'id',
                                                    'user_id': 'user_id',
                                                    'name'   : 'name',
                                                    'project_id':'project_id',
                                                },

                          'nested_objects': [],

                          'key_map_for_nested_schemes': {},
                            'db_col_types':{
                                'id': Column(String(36), primary_key=True),
                                'user_id':Column(BigInteger, nullable=False),
                                'name':Column(Unicode, nullable=True),
                                'project_id': Column(Integer, nullable=True),
                               
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

        if is_save:
            filters.new_filter(
                ConditionTypeEQ(), 
                self.primary_key, 
                db_record[self.primary_key] 
            )
        else:

            for i_secondary_key in self.secondary_key:
                filters.new_filter(
                    ConditionTypeEQ(), 
                    i_secondary_key, 
                    db_record[i_secondary_key] 
                )

        return filters
    
    def new_primary_key(self):
        return str(uuid.uuid1())

