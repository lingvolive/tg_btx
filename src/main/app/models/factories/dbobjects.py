
from abc import ABC, abstractmethod

class DBObject(ABC):
    __scheme = None
    
    def __init__(self, data : dict = None) -> None:
        
        self.fill_from_dict(data)
        self._is_modified = False
        self._is_readable = True
        
    @abstractmethod
    def view(self, app_resources):
        pass

    @classmethod
    def set_scheme(cls, scheme ):
        cls.__scheme = scheme
    
    @classmethod
    def get_scheme(self):
        return self.__scheme

    def _get_value(self, attr_name):
        return getattr(self, attr_name)       
    
    def _set_value(self, attr_name, value):
        self.modified()
        setattr(self, attr_name, value)
    
    def fill_from_dict(self, params : dict):
        if(params is None):
            return
        
        for key, value in params.items():
            private_key = f'_{key}'
            #if(hasattr(self, private_key)):
            self._set_value(private_key, value)

    def to_dict(self):
        pass

    def is_modified(self) -> int:
        return self._is_modified

    def is_readable(self) -> int:
        return self._is_readable

    def readable(self) -> None:
        self._is_readable = True
    
    def modified(self) -> None:
        self._is_modified = True

    def reset_modified(self) -> None:
        self._is_modified = False

    
        

