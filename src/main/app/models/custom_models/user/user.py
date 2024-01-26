from app.models.factories.dbobjects import DBObject
from app.models.custom_models.user.role import Role
 
class User(DBObject):

    def __init__(self, data : dict = None ) -> None:

        super().__init__(data)

        self._roles = []
        self._manager = None
        self._manager_id = 0
        self._is_blocked = False

    @property
    def roles(self):
        return self._roles
    
    @roles.setter
    def roles(self, value):
        self._roles = value

    @property
    def manager(self):
        return self._manager
    
    @manager.setter
    def manager(self, value):
        if(value is None):
            self.manager_id = 0
        elif(value.id == None):
            self.manager_id = 0
        else:
            self.manager_id = value.id

        self._manager = value

    def add_role(self, role):
        role_exist = self.has_role(role.name)

        if(not role_exist):
            self.roles.append(role)

    def delete_role(self, role_name):
        numbers_roles = len(self._roles)
        for idx in range(numbers_roles):
            role = self._roles[ numbers_roles - idx - 1 ]
            if(role_name == role.name):
                del self._roles[numbers_roles - idx - 1]


    def has_role(self, role_name):
        role_exist = False
        for role_item in self.roles:
            if(role_item.name == role_name):
                role_exist = True
                break

        return role_exist


    def view(self, app_resources):

        user_view = ''
        if(self.full_name_ext is not None):
            user_view = self.full_name_ext
        elif(self.full_name is not None):
            user_view = self.full_name
        else:
            user_view = f'id: {self.id}'

        if( not self.is_auth):
            user_view = f'{user_view} ({app_resources.strNotAuth})'

        return user_view


    def profile_text(self, app_resources):
        
        profile_text = []
        if(not self.is_auth):
            profile_text.append(app_resources.strUserNotAuth)
            profile_text.append(' ')

        role_items = Role.get_roles(app_resources)
        role_lines = []
        for role in self.roles:
            role_lines.append(role_items[role.name])
            
        role_text = ', '.join(role_lines)
        
        if(self.manager is None):
            manager_name = None
        else:
            manager_name = self.manager.view(app_resources)

        profile_lines = [
            (app_resources.strUserName, self.full_name),
            (app_resources.strEmail, self.email),
            (app_resources.strUserFIO, self.full_name_ext),
            (app_resources.strPhone, self.phone_ext),
            (app_resources.strRoles, role_text),
            (app_resources.strManager, manager_name),
        ]
        
        profile_lines_text = [ self._format_profile_string(
                                    profile_line_item[0], 
                                    profile_line_item[1],
                                    app_resources
                                )
                            for profile_line_item in profile_lines
        ]

        profile_text = profile_text + profile_lines_text
 
        #profile_text.append(f'{app_resources.strRoles}:{self.user.name}')
        
        return '\n'.join(profile_text).strip()
    
    def _format_profile_string(self, key, value, app_resources):
        value = self._set_def_value_if_empty(value, app_resources)
        return f'- {key}: {value}'
    
    def _set_def_value_if_empty(self, line: str, app_resources ):

        if(line is None or line == ''):
            return app_resources.strNotSpecified
        else:
            return line

        
        

        



 