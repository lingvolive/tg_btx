import time
from datetime import datetime
from app.models.factories.dbobjects import DBObject
from app.models.factories.enum_domain_objects import domainObjectTypes 
 
class SessionLog(DBObject):

    cls_type = domainObjectTypes.SessionLog

    def __init__(self, data : dict = None ) -> None:

        super().__init__(data)
        
        self._is_readable = False
        self._start_time = None
        self.processed     = False
        self.answered_text = ''
        self.elapsed_time  = 0
        self.content = ''

    def view(self, app_resources):
        return self.content_type

    def start_log(self):

        self._start_time    = time.monotonic()
        self.user_id       = self._message.user_id
        self.chat_id       = self._message.chat_id
        self.content_type  = self._message.message_type.value
        self.date          = datetime.utcnow()
        self.message_id    = self._message.tg_message.message_id
        self.message_data  = self._message.callback_data
        self.content       = self._message.get_content()
      
    def finish_log(self, answered_text):

        self.answered_text = answered_text
        self.processed     = True
        self.elapsed_time = time.monotonic() - self._start_time

        
        
    
