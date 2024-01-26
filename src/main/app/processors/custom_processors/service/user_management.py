
from app.models.factories.domain_objects_factory import DomainClassFactory
from app.models.factories.enum_domain_objects import domainObjectTypes
from app.store.factories.datamapper_factory import DatamapperFactory
from app.store.factories.schemes_factory import SchemeFactory
from app.store.filters.filter import Filters, ConditionTypeEQ
from app.store.sorting.sorting import Sorting
from app.store.paging.paging import Paging


class UserManagement():

    def __init__(self, current_user = None) -> None:
        
        self._user         = None
        self._session      = None
        self._current_user = current_user

    @property
    def user(self):
        return self._user
    
    @property 
    def session(self):
        return self._session
    
    @user.setter
    def user(self, value):
        self._user = value

    @session.setter
    def session(self, value):
        self._session = value
        
    def add_role(self, user, role_name):

        domain_factory = DomainClassFactory()
        role = domain_factory.create(
            domainObjectTypes.Role, 
            {'name': role_name, 'user_id': user.id}
        )
        user.is_auth = True
        user.is_wait_confirmation = False
        user.add_role(role)

    def delete_role(self, user, role_name):

        user.delete_role(role_name)

        if(len(user.roles) == 0):
            user.is_auth = False
            user.is_wait_confirmation = True

    def block(self):

        if(self._user is None):
            return
        
        self._user.roles = []
        self._user.manager_id = 0
        self._user.is_blocked = True

    async def read_roles_by_name(self, role_name, sorting_field = None,
                          page = None, page_size = None):

        datamapper  = DatamapperFactory('local').get()
        scheme_role = SchemeFactory('local').get(domainObjectTypes.Role)

        filters = Filters()
        sorting = None
        paging  = None
        filters.new_filter(ConditionTypeEQ(), 'name', role_name)

        if(page is not None):
            Paging(page, page_size)

        if(sorting_field is not None):
            sorting = Sorting()
            for field, direction in sorting_field.items():
                sorting.new_sorting(field, direction)


        roles = await datamapper.read(scheme_role, filters=filters, 
                                      sorting=sorting, paging=paging)

        return roles


    async def read_by_id(self, user_id, read_session = False):

        if(self._current_user is not None and self._current_user.id == user_id):
            self._user = self._current_user
            return self._user
        
        if(read_session):

            user = DomainClassFactory.create(
                        domainObjectTypes.User, 
                        {'id':user_id}
            )
            self._session = await self._read_session(user)
            self._user   = self._session.user
        else:
            self._user = await self._read_user(user_id)
            self._session = None

        if(self._user.manager_id is not None and self._user.manager_id > 0):
            self._user.manager = await self.read_bitrix_user_by_id(self._user.manager_id)

        return self._user
    
    async def read_bitrix_user_by_id(self, user_id):

        user_bitrix = DomainClassFactory.create(
                        domainObjectTypes.UserBitrix, 
                        {'id':user_id}
        )

        datamapper = DatamapperFactory('local').get()
        await datamapper.fill_instance_from_db(user_bitrix)

        return user_bitrix
    
    async def read_project_by_id(self, project_id):

        project = DomainClassFactory.create(
                        domainObjectTypes.Project, 
                        {'id':project_id}
        )

        datamapper = DatamapperFactory('local').get()
        await datamapper.fill_instance_from_db(project)

        return project
    

    async def save(self):
        
        datamapper = DatamapperFactory().get()

        if(self._session is not None):
            datamapper.add_dataobject(self._session)
        elif(self._user is not None):
            datamapper.add_dataobject(self._user)
        elif(self._current_user is not None):
            datamapper.add_dataobject(self._current_user)

        await datamapper.write_dataobjects_to_db()

    async def _read_user(self, user_id):
        
        user = DomainClassFactory.create(
            domainObjectTypes.User, 
            {'id':user_id}
        )

        datamapper = DatamapperFactory('local').get()
        await datamapper.fill_instance_from_db(user)

        return user
    
    async def _read_session(self, user):
        
        session = DomainClassFactory.create(
            domainObjectTypes.Session, 
            {'user':user}
        )

        datamapper = DatamapperFactory('local').get()
        await datamapper.fill_instance_from_db(session)

        return session

