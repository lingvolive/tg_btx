from sqlalchemy import Column, Unicode, BigInteger, String, Boolean

from app.store.scheme import Scheme
from app.store.filters.filter import Filters, ConditionTypeEQ


class SchemeUserBitrix(Scheme):

    def __init__(self, dbobject_type_id) -> None:

        super().__init__(dbobject_type_id)
    
    def prepare_describe(self):
        
        self._describe = {
            'name'         : 'UserBitrix',
            'table'        : 'users_bitrix',
            'primary_key'  : 'id',
            'secondary_key': [],
            'nested_objects': {}, 
            'key_map_for_nested_attributes': {},
            
            'db_rules': {  'property_to_db_col_map' :{
                                'id'           :'id',
                                'name'         :'name',
                                'last_name'    :'last_name',
                                'email'        :'email',
                                'is_blocked'  : 'is_blocked',
                            },
                           'blocked_from_being_read_from_db':['id', 
                                                              'name',
                                                              'last_name', 
                                                              'email', 
                                                            
                                                            ],

                            'db_col_types':{
                                'id': Column(BigInteger, primary_key=True),
                                'name':Column(Unicode, nullable=True),
                                'last_name':Column(Unicode, nullable=True),
                                'email':Column(String, nullable=True),
                                'is_blocked':Column(Boolean, nullable=True,),
                            },
                        },
        }
   
    def extract_schema_from_instance(self, cls_instance, owner  = None) -> dict:
        return self.extract_schema_from_instance_default(cls_instance)
    
    def fill_instance(self, cls_instance, record:dict):
        self.fill_instance_default(cls_instance, record)

    def get_primary_key_values_pairs(self, db_record : dict, is_save: bool) -> list :
        filters = []
        filters = Filters()

        if(db_record[self.primary_key] is None):
            db_record[self.primary_key] = 0
        filters.new_filter(ConditionTypeEQ(), self.primary_key, db_record[self.primary_key] )

        return filters
    
    def new_primary_key(self):
        raise NotImplementedError

