
from app.models.factories.enum_domain_objects import domainObjectTypes
from app.store.factories.schemes_factory import SchemeFactory
from app.models.factories.dbobjects import DBObject

from app.models.custom_models.user.user import User
from app.models.custom_models.session.session import Session
from app.models.custom_models.session.session_log import SessionLog
from app.models.custom_models.user.role import Role
from app.models.custom_models.user.user_bitrix import UserBitrix
from app.models.custom_models.project.project import Project

scheme_domain_class_map = {
    domainObjectTypes.User : User,
    domainObjectTypes.Session : Session,
    domainObjectTypes.SessionLog : SessionLog,
    domainObjectTypes.Role : Role,
    domainObjectTypes.UserBitrix : UserBitrix,
    domainObjectTypes.Project : Project,
}

class DomainClassFactory:

    @staticmethod
    def create_from_scheme(scheme, constructor_args : dict):
       
        return DomainClassFactory.create(
            scheme.get_dbobject_type_id(), 
            constructor_args
        )

    @staticmethod
    def create(
        cls_type: domainObjectTypes, 
        constructor_args : dict = {} 
    ) -> DBObject:

        cls = scheme_domain_class_map.get(cls_type)
        assert cls is not None, f'Class type {cls_type.value} is not supported.'


        assert not isinstance(cls, DBObject), \
            f'Class "{cls.__name__}" does not inherit from DBObject class'
       
        if(cls.get_scheme() == None):
            scheme      = SchemeFactory().get(cls_type)
            cls.set_scheme(scheme)
            DomainClassFactory.add_scheme_properties_to_cls(cls, scheme)

        instance = cls(constructor_args)
        
        return instance

    @staticmethod
    def add_scheme_properties_to_cls(cls : type, scheme):

        describe = scheme.describe()

        for key in describe['db_rules']['property_to_db_col_map'].keys():
                DomainClassFactory.add_property( cls,  key )

    @staticmethod
    def add_property( cls : type,  key :str ):

        def make_getter(attr_name):
            def getter(self):
                return self._get_value(attr_name)

            return getter

        def make_setter(attr_name):
            def setter(self, value):
                return self._set_value(attr_name, value)

            return setter

        private_key = f'_{key}'
        property_fn = property( make_getter(private_key), make_setter(private_key) )
        setattr(cls, private_key, None)
        setattr(cls, key, property_fn)
      
   


