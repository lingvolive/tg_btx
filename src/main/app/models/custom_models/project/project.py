from typing import Union
from app.models.factories.dbobjects import DBObject
 
class Project(DBObject):

    def __init__(self, data: dict = None ) -> None:

        super().__init__(data)

    def view(self, app_resources):
        return self.name

  
 