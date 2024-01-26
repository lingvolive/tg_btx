import json
import uuid
from app.store.scheme import Scheme
from app.store.filters.filter import Filters, ConditionTypeEQ

from sqlalchemy import (
    Column, Unicode, Integer, BigInteger, 
    Float, TEXT, String, DateTime, Boolean
)

class SchemeSessionLog(Scheme):

    def __init__(self, dbobject_type_id) -> None:
        super().__init__(dbobject_type_id)
      
    def prepare_describe(self):

        self._describe = {
            'name': 'sessions_log',
            'table' : 'sessions_log',
            'primary_key':'id',
            'secondary_key':[],
            'db_rules':{ 'property_to_db_col_map':{
                                                    'id'     : 'id',
                                                    'user_id': 'user_id',
                                                    'chat_id': 'chat_id',
                                                    'content_type':'content_type',
                                                    'date': 'date',
                                                    'elapsed_time': 'elapsed_time',
                                                    'message_id':'message_id',
                                                    'content':'content',
                                                    'message_data':'message_data',
                                                    'answered_text':'answered_text',
                                                    'processed':'processed'
                                                },

                            'db_col_types':{
                                'id': Column(String(36), primary_key=True),
                                'user_id':Column(BigInteger, nullable=False),
                                'chat_id':Column(BigInteger, nullable=False),
                                'content_type':Column(String, nullable=False),
                                'content':Column(TEXT, nullable=True),
                                'date':Column(DateTime, nullable=False),
                                'elapsed_time':Column(Float, nullable=True),
                                'message_id':Column(Integer, nullable=False),
                                'message_data':Column(TEXT, nullable=True),
                                'answered_text':Column(TEXT, nullable=True),
                                'processed':Column(Boolean, nullable=True),
                               
                            },
                        },
            
        }

 
    def extract_schema_from_instance(self, cls_instance , owner  = None) -> dict:
        scheme_struct = self.extract_schema_from_instance_default(cls_instance)
        scheme_struct['message_data']= json.dumps(cls_instance.message_data)

        return scheme_struct

    def fill_instance(self, cls_instance, record:dict):
        self.fill_instance_default(cls_instance, record)

        json_str = record.get('data')
        if(not isinstance(json_str, str) ):
            cls_instance.data = {}
        else:
            cls_instance.data = json.loads(json_str)

    def get_primary_key_values_pairs(self, db_record : dict, is_save: bool ) -> list :

        filters = Filters()
        filters.new_filter(ConditionTypeEQ(), self.primary_key, db_record[self.primary_key] )

        return filters
    
    def new_primary_key(self):
        return str(uuid.uuid1())

