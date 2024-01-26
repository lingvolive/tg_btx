from abc import ABC, abstractmethod

class Scheme(ABC):

    def __init__(self, dbobject_type_id ) -> None:
        super().__init__()
        self._dbobject_type_id = dbobject_type_id
       
        self.prepare_describe()
        self.define_properties()

    def __str__(self):
        return type(self).__name__

    def define_properties(self):
        describe = self.describe()

        def make_getter(attr_name):

            def getter(self):
                return self._get_value(attr_name)

            return getter

        for key, _ in describe.items():
            property_fn = property( make_getter(key) )
            setattr(self.__class__, key, property_fn)
  
    def _get_value(self, attr_name):
        return self.describe()[attr_name]

    def get_dbobject_type_id(self):
        return self._dbobject_type_id

    def get_map_db_col_to_attr(self):

        property_to_db_col_map = self.db_rules['property_to_db_col_map'].items()
        return {db_col:attr_name for attr_name, db_col in property_to_db_col_map }

    def db_col_names(self):
        return self.db_rules['property_to_db_col_map'].values()
    
    def get_db_col_types(self):
        return self.db_rules['db_col_types']

    def fill_instance_default(self, cls_instance, record : dict):

        map_db_col_to_attr = self.get_map_db_col_to_attr()
        
        for db_col, value in record.items():

            attr_name = map_db_col_to_attr.get(db_col)

            if(attr_name is None):
                continue

            if(not hasattr(cls_instance, attr_name) ):
                continue

            current_attr_value = getattr(cls_instance, attr_name)
            
            if( self.is_property_blocked_from_being_read_from_db(attr_name) 
                and not self._is_value_empty(current_attr_value)
            ):
                continue

            
            setattr(cls_instance, attr_name, value )

    def extract_schema_from_instance_default(self, cls_instance) -> dict:

        data_item = {}
         
        for attr_name, db_col_name in self:
            
            attr_value = None
            
            if hasattr(cls_instance, attr_name):
                attr_value = getattr(cls_instance, attr_name )
                
            data_item[db_col_name] = attr_value

        return data_item

    def is_property_blocked_from_being_read_from_db(self, property : str) -> bool:

        blocked_from_being_read_from_db = self.describe()['db_rules'].get('blocked_from_being_read_from_db', [])

        return property in blocked_from_being_read_from_db
     
    def describe(self):
        return self._describe
    
    def __iter__(self):

        for attr_name, db_col_name in self.db_rules['property_to_db_col_map'].items():
            yield attr_name, db_col_name

    def __getitem__(self, attr_name):
        
        if attr_name not in self._scheme.keys():
           # raise IndexError(key)
           return None
            
        return self.__scheme[attr_name]
    
    def get_nested_object_attributes(self):

        if(hasattr(self, 'nested_objects')):
            return self.nested_objects
        else:
            return {}

    def extract_nested_key_row(self, owner_attribute : str, record : dict ) -> dict:
        assert hasattr(self, 'key_map_for_nested_attributes'), \
                f'The class {type(self)} does not have key_map_for_nested_attributes'
        
        key_map = self.key_map_for_nested_attributes[owner_attribute]
        nested_row = {}

        for item_key_map in key_map:
            nested_row[ item_key_map['slave_attr'] ] =\
                  record[ item_key_map['owner_attr'] ]

        return nested_row
    
    def get_nested_scheme_by_attribute(self, attribute):

        nested_objects = self.get_nested_object_attributes()

        return nested_objects[attribute]['scheme']

    def _is_value_empty(self, value):
    
        return value is None or value == '' or value == 0 

    @abstractmethod
    def prepare_describe(self):
        pass

    @abstractmethod
    def fill_instance(self, cls_instance, record:dict) -> None:
        pass
    
    @abstractmethod
    def extract_schema_from_instance(self, cls_instance, owner = None) -> dict:
        pass

    @abstractmethod
    def new_primary_key(self):
        pass

    