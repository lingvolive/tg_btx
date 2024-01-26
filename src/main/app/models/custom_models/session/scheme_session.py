import json
import uuid
from app.store.scheme import Scheme
from app.models.custom_models.user.scheme_user import SchemeUser
from app.models.factories.enum_domain_objects import domainObjectTypes
from app.resources.enums import processorsTypes
from app.store.filters.filter import Filters, ConditionTypeEQ

from sqlalchemy import Column, Unicode, Integer, BigInteger, TEXT, String
 

class SchemeSession(Scheme):

    def __init__(self, dbobject_type_id) -> None:

        super().__init__(dbobject_type_id)
      
    def prepare_describe(self):

        self._describe = {
            'name': 'sessions',
            'table' : 'sessions',
            'primary_key':'id',
            'secondary_key':['user_id'],
            'nested_objects': { 
                                 'user':{ 
                                    'scheme': SchemeUser(domainObjectTypes.User),

                                 }
                            },
            'key_map_for_nested_attributes': { 'user': [
                                            {
                                              'owner_attr': 'user_id', 
                                              'slave_attr': 'id'
                                            } 
                                        ],
                                       
                                },
            'db_rules':{ 'property_to_db_col_map':{
                                                    'id'     : 'id',
                                                    'user_id': 'user_id',
                                                    'data'   : 'data',
                                                    'state_id':'state_id',
                                                },

                            'db_col_types':{
                                'id': Column(String(36), primary_key=True),
                                'user_id':Column(BigInteger, nullable=False),
                                'data':Column(TEXT, nullable=True),
                                'state_id': Column(Integer, nullable=False),
                               
                            },
                        },
            
        }

    def extract_schema_from_instance(self, cls_instance , owner  = None) -> dict:

        scheme_struct = self.extract_schema_from_instance_default(cls_instance)

        scheme_struct['user_id']  = cls_instance.user.id
        scheme_struct['data']     = json.dumps(cls_instance.data)

        state_id = cls_instance.state_id
        if(state_id is None):
            state_id = processorsTypes.NONE
        scheme_struct['state_id'] = state_id.value

        return scheme_struct

    def fill_instance(self, cls_instance, record:dict):
        
        self.fill_instance_default(cls_instance, record)

        state_id = record.get('state_id')
        if(state_id is None):
            state_id = processorsTypes.NONE
        else:
            state_id = processorsTypes(state_id)

        cls_instance.state_id = state_id
        cls_instance.user = record.get('user')

        json_str = record.get('data')
        if(not isinstance(json_str, str) ):
            cls_instance.data = {}
        else:
            cls_instance.data = json.loads(json_str)
        #cls_instance.games = record.get('games')

    def get_primary_key_values_pairs(self, db_record : dict, is_save: bool ) -> list :

        filters = Filters()

        for i_secondary_key in self.secondary_key:
            filters.new_filter(ConditionTypeEQ(), i_secondary_key, db_record[i_secondary_key] )

        return filters
    
    def new_primary_key(self):
        return str(uuid.uuid1())

