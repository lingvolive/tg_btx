
from abc import ABC, abstractmethod
from app.services.metaclass import SingletonByID
from app.store.factories.storage_config_factory import (
    DBConfig, 
    DBConfigCVS, 
    DBConfigPostgres, 
    DBConfigFactory
)
from app.models.custom_models.user.scheme_user import SchemeUser
from app.models.custom_models.session.scheme_session import SchemeSession 
from app.models.custom_models.session.scheme_session_log import SchemeSessionLog
from app.models.custom_models.user.scheme_role import SchemeRole 
from app.models.factories.enum_domain_objects import domainObjectTypes
from app.models.custom_models.user.scheme_user_bitrix import SchemeUserBitrix
from app.models.custom_models.project.scheme_project import SchemeProject

class MapClassNameToScheme(ABC):
    
    @staticmethod
    @abstractmethod
    def get_map():
        pass

class MapClassNameToSchemeCommon(MapClassNameToScheme):
        
    @staticmethod
    def get_map():

        return {
            domainObjectTypes.User    : SchemeUser,
            domainObjectTypes.Session : SchemeSession,
            domainObjectTypes.SessionLog : SchemeSessionLog,
            domainObjectTypes.Role : SchemeRole,
            domainObjectTypes.UserBitrix : SchemeUserBitrix,
            domainObjectTypes.Project : SchemeProject,

        }

class SchemeFactory(metaclass=SingletonByID):

    _instances = {}

    def __init__(self, id:str = 'local', db_config: DBConfig = None) -> None:

        if(db_config == None):
            db_config = DBConfigFactory(id = id).get()

        self._id = id
        
        if( isinstance(db_config, DBConfigCVS) 
           or isinstance(db_config, DBConfigPostgres)):
            self._scheme_map = MapClassNameToSchemeCommon.get_map()
        else:
            ValueError(f'Unsupported DBConfig type "{db_config.__name__}"')

    def __iter__(self):

        if(len(self._instances) == 0):
            for object_type in self._scheme_map.keys():
                self.get(object_type)

        for instance in self._instances.values():
            yield instance

    def get(self, cls_type: domainObjectTypes ):

        if( self._instances.get(cls_type) == None):
            self._instances[cls_type] = self._scheme_map[cls_type](cls_type)
      
        return self._instances.get(cls_type)
    
    def get_scheme_map(self):
        return self._scheme_map