
from app.models.factories.dbobjects import DBObject
 
class UserBitrix(DBObject):

    def __init__(self, data : dict = None ) -> None:

        super().__init__(data)

        self._is_blocked = False

    def view(self, app_resources):

        last_name = '' if self.last_name is None else self.last_name
        name = '' if self.name is None else self.name

        user_view = f'{last_name} {name}'
       
        return user_view

    def profile_text(self, app_resources):
        
        profile_text = []
        
        return '\n'.join(profile_text).strip()
    
    
        
        

        



 