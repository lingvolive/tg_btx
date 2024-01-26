
from abc import ABC, abstractmethod

class FilterGroupTypes(ABC):

    def __init__(self) -> None:
        super().__init__()

class FilterGroupTypeOR(FilterGroupTypes):

    def __init__(self) -> None:
        super().__init__()

class FilterGroupTypeAND(FilterGroupTypes):

    def __init__(self) -> None:
        super().__init__()

class ConditionTypes(ABC):

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def check_value(self, value):
        return True
    
    def __str__(self):

        return type(self).__name__

class ConditionTypeEQ(ConditionTypes):

    def __init__(self) -> None:
        super().__init__()

    def check_value(self, value):
        return True
    
class ConditionTypeNEQ(ConditionTypes):

    def __init__(self) -> None:
        super().__init__()

    def check_value(self, value):
        return True
    
    
class ConditionTypeGT(ConditionTypes):

    def __init__(self) -> None:
        super().__init__()

    def check_value(self, value):
        return True
   
    
class ConditionTypeGTE(ConditionTypes):

    def __init__(self) -> None:
        super().__init__()

    def check_value(self, value):
        return True
   
    
class ConditionTypeLT(ConditionTypes):

    def __init__(self) -> None:
        super().__init__()

    def check_value(self, value):
        return True
    
    
class ConditionTypeLTE(ConditionTypes):

    def __init__(self) -> None:
        super().__init__()

    def check_value(self, value):
        return True
    

class ConditionTypeIN(ConditionTypes):

    def __init__(self) -> None:
        super().__init__()

    def check_value(self, value):
        return True
     
    
class ConditionTypeLike(ConditionTypes):

    def __init__(self) -> None:
        super().__init__()

    def check_value(self, value):
        return True
    def get_query_of_condition(self):
        pass

class ConditionTypeVectorSimilarity(ConditionTypes):

    def __init__(self) -> None:
        super().__init__()

    def check_value(self, value):
        return True
    def get_query_of_condition(self):
        pass

class Filter():

    def __init__(self, filter_type = None, field_name = None, value = None, value_to = None ) -> None:
        self._field_name = field_name
        self._value = value
        self._value_to = value_to
        self._filter_type = filter_type

    def __str__(self):

        return str( 
                {'field_name':self._field_name, 
                 'value':self._value,
                 'condition': str(self._filter_type)
                 } 
            )

    @property
    def field_name(self):
        return self._field_name
    
    @field_name.setter
    def field_name(self, value):
        self._field_name = value

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        self._value = value

    @property
    def value_to(self):
        return self._value_to
    
    @value_to.setter
    def value_to(self, value):
        self._value_to = value

    @property
    def filter_type(self):
        return self._filter_type
    
    @filter_type.setter
    def filter_type(self, value):
        self._filter_type = value

    def symbol_quote(self):
        if(isinstance(self.value, str)):
            return '"'
        else:
            return ''
    
    def set(self, field_name:str, value, condition:ConditionTypes ):
        self.field_name = field_name
        self.value = value
        self.condition = condition


class Filters():

    def __init__(self, group_type : FilterGroupTypes = None) -> None:
        self._filters = []
        self._group_type = FilterGroupTypeAND() if group_type is None else group_type

    def __str__(self):

        filters_str = []
        for filter in self._filters:
            filters_str.append(str(filter))

        return str(filters_str)
    
    def is_empty(self):
        return len(self._filters) == 0
    
    def append_filter(self, filter):
        self._filters.append(filter)

    def get_filters(self):
        return self._filters
    
    def get_condition_type(self):
        return self._group_type

    def new_filter(self, condition:ConditionTypes, field_name:str, value ):
        filter = Filter(condition, field_name, value)
        self.append_filter(filter)
        return filter

    def reset(self):
        self._filters = []

    def find_filter_by_field(self, field_name):
        for filter in self._filters:
            if filter.field_name == field_name:
                return filter
            
        return None