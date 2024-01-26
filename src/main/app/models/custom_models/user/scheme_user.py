


from sqlalchemy import Column, Unicode, BigInteger, String, Boolean

from app.models.factories.enum_domain_objects import domainObjectTypes
from app.store.scheme import Scheme
from app.store.filters.filter import Filters, ConditionTypeEQ
from app.models.custom_models.user.scheme_role import SchemeRole
from app.models.custom_models.user.scheme_user_bitrix import SchemeUserBitrix


class SchemeUser(Scheme):

    def __init__(self, dbobject_type_id) -> None:

        super().__init__(dbobject_type_id)
    
    def prepare_describe(self):
        
        self._describe = {
            'name'         : 'User',
            'table'        : 'users',
            'primary_key'  : 'id',
            'secondary_key': [],
            'nested_objects': { 'roles':{
                                    'scheme': SchemeRole(domainObjectTypes.Role) 
                                }, 
                                'manager':{
                                    'scheme':SchemeUserBitrix(domainObjectTypes.UserBitrix) 
                                }
                                
            }, 
            
            'key_map_for_nested_attributes': {
                    'roles'   : [ {'owner_attr': 'id', 'slave_attr': 'user_id'} ],
                    'manager' : [ {'owner_attr': 'manager_id', 'slave_attr': 'id'} ],

            },
            
            'db_rules': {  'property_to_db_col_map' :{
                                'id'           :'id',
                                'full_name'    :'full_name',
                                'language_code':'language_code',
                                'url'          :'url',
                                'language'     :'language',
                                'phone'        :'phone',
                                'email'        :'email',
                                'full_name_ext': 'full_name_ext',
                                'phone_ext'    : 'phone_ext',
                                'manager_id'  : 'manager_id',
                                'is_auth'     : 'is_auth',
                                'is_blocked'  : 'is_blocked',
                                'is_wait_confirmation' : 'is_wait_confirmation',
                            },
                           'blocked_from_being_read_from_db':['id', 
                                                              'full_name', 
                                                              'language_code', 
                                                              'url',
                                                              'phone'
                                                              ],

                            'db_col_types':{
                                'id': Column(BigInteger, primary_key=True),
                                'full_name':Column(Unicode, nullable=True),
                                'language_code':Column(String, nullable=True),
                                'url': Column(Unicode, nullable=True),
                                'language':Column(String, nullable=True),
                                'last_name':Column(Unicode, nullable=True),
                                'manager_id':Column(BigInteger, nullable=True),
                                'email':Column(String, nullable=True),
                                'phone':Column(String, nullable=True),
                                'full_name_ext':Column(Unicode, nullable=True),
                                'phone_ext':Column(String, nullable=True),
                                'is_auth':Column(Boolean, nullable=True),
                                'is_blocked':Column(Boolean, nullable=True,),
                                'is_wait_confirmation':Column(Boolean, nullable=True),
                            },
                        },
        }
   
    def extract_schema_from_instance(self, cls_instance, owner  = None) -> dict:
        return self.extract_schema_from_instance_default(cls_instance)
    
    def fill_instance(self, cls_instance, record:dict):
        self.fill_instance_default(cls_instance, record)

        if(cls_instance.language is None):
            cls_instance.language = cls_instance.language_code

        cls_instance.roles = record.get('roles', [])
        cls_instance.manager = record.get('manager')
    
    def get_primary_key_values_pairs(self, db_record : dict, is_save: bool) -> list :
        filters = []
        filters = Filters()

        if(db_record[self.primary_key] is None):
            db_record[self.primary_key] = 0
        filters.new_filter(ConditionTypeEQ(), self.primary_key, db_record[self.primary_key] )

        return filters
    
    def new_primary_key(self):
        raise NotImplementedError

