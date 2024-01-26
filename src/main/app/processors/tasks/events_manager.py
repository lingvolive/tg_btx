
from threading import Lock
from enum import Enum, auto

#from app.services.logging import setup_logger

from app.processors.tasks.task import (
    TaskNotifyEventNewUser,
    TaskNotifyEventUserRegistered,
)

from app.processors.tasks.task_labor_cost_report import TaskGenerateLaborCostReport

#logger = setup_logger(__name__)

class eventTypes(Enum):
    NEW_USER = auto()
    USER_REGISTERED = auto()
    LABOR_COST_REPORT = auto()


class SingletonEvents(type):
    
    _instances = {}
    _lock      = Lock()
    
    def __call__(cls, *args, **kwargs):
        
        #with cls._lock:
       
        if(cls not in cls._instances):
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        
        return cls._instances[cls] 

class EventsManager(metaclass=SingletonEvents):

    def __init__(self, task_queue = None) -> None:
        self._event_type_to_task_map = {}
        self._task_queue = task_queue

        self.register_event(eventTypes.NEW_USER       , TaskNotifyEventNewUser)
        self.register_event(eventTypes.USER_REGISTERED, TaskNotifyEventUserRegistered)
        self.register_event(eventTypes.LABOR_COST_REPORT, TaskGenerateLaborCostReport)
    
    def register_event(cls, event_type: eventTypes, task_cls):
        cls._event_type_to_task_map[event_type] = task_cls

    async def notify(self, event_type: eventTypes, params: dict):
        #logger.debug(f'NOTIFY:{event_type.name}')
        
        task_cls = self._event_type_to_task_map.get(event_type)
        assert task_cls is not None, \
                f'Event type: "{event_type}" is not supported'
        
        task = task_cls(params)
        await self._task_queue.put(task)