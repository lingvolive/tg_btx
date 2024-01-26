from threading import Lock

class SingletonBase(type):
    
    _instances = {}
    _lock      = Lock()
    
    def __call__(cls, *args, **kwargs):
        
        #with cls._lock:
       
        if(cls not in cls._instances):
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        
        return cls._instances[cls]
    

class SingletonByID(type):
    
    _instances_by_id = {}
    _lock      = Lock()
    
    def __call__(cls, id = 'local', *args, **kwargs):
        
        #with cls._lock:
        cls_id = f'{cls.__name__}_{id}'
    
        if(cls_id not in cls._instances_by_id):
                instance = super().__call__(*args, **kwargs)
                cls._instances_by_id[cls_id] = instance
            
        return cls._instances_by_id[cls_id]



