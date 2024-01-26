from typing import Union
from app.models.factories.dbobjects import DBObject
 
class Role(DBObject):

    def __init__(self, data: dict = None ) -> None:

        super().__init__(data)

    def view(self, app_resources):
        return self.name

    @staticmethod
    def get_roles(app_resources):
        return {
            'admin': app_resources.strRoleAdmin,
            'manager': app_resources.strRoleManager,
            'employee': app_resources.strRoleEmployee,
        }

 