#from typing import Annotated
from app.models.factories.dbobjects import DBObject
from app.models.custom_models.user.user import User
from app.telegram_bot.bot_message import tgUserMassage
from app.models.factories.enum_domain_objects import domainObjectTypes 
 
class Session(DBObject):

    cls_type = domainObjectTypes.Session

    def __init__(self, data: dict = None ) -> None:
        super().__init__(data)

        self.time_zone = 3
       
    def view(self, app_resources):
        return self.id
    
    @property
    def message(self) -> tgUserMassage:
        return self._message
    
    @message.setter
    def message(self, value):
        self._message = value

    @property
    def user(self) -> User:
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

   