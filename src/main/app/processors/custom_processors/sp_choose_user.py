from abc import ABC, abstractmethod

from app.resources.enums import processorsTypes
from app.processors.state_processor import StateProcessor
from app.processors.custom_processors.service.user_management import UserManagement
from app.processors.custom_processors.service.helpers import SPUserManagementHelper
from app.models.custom_models.session.user_settings_manager import UserSettingsManager
from app.models.factories.enum_domain_objects import domainObjectTypes
from app.store.factories.schemes_factory import SchemeFactory
from app.store.factories.datamapper_factory import DatamapperFactory
from app.store.filters.filter import Filters, ConditionTypeEQ
from app.store.sorting.sorting import Sorting
from app.store.paging.paging import Paging

from app.telegram_bot.bot_interface import (
    tgButton,
    tgInlineMenu
)

class ItemChooser(StateProcessor, ABC):

    def __init__(
            self, 
            session, 
            chain:dict, 
            processor_type:processorsTypes,
          
    ) -> None:
        
        super().__init__(session, chain, processor_type)

        self._page_size = 8
        self._count_buttons_in_row = 1
        
        self._action_id = ''
        self._menu_id   = ''
        self._pager_settings_name = ''
        self._title = ''

        self.init()
    
    @abstractmethod
    def get_resetting_settings(self):
        return {self._pager_settings_name:1}
    
    @abstractmethod
    def init(self):
        self._filters = None
        self._sorting = None
        self._domain_object_type = None

    @abstractmethod
    async def _process_hook(self, action_id, settings_manager):
        pass
    
    async def pre_process(self):
        settings_manager = UserSettingsManager(self.session)
        page  = settings_manager.get_setting(self._pager_settings_name, 1)

        menu = await self._get_menu_by_page(
            self._domain_object_type, 
            self._filters, 
            self._sorting, 
            page
        )   
          
        message_text = []
        message_text.append(f'*{self._title}*\n')

        await self.session.message.send('\n'.join(message_text), menu)

        return self.id
    
    async def process(self):

        state_id =  await self._default_inline_keyboard_handler()

        if( not state_id == self.id ):
            return state_id

        if( not self.session.message.is_inline() or 
           not self._menu_id == self.session.message.get_menu_id()
        ):
            return state_id

        settings_manager = UserSettingsManager(self._session)
        action_id = self.session.message.get_action_id()

        hook_state_id = await self._process_hook(action_id, settings_manager)
        if(hook_state_id is not None):
            return hook_state_id

        if( action_id == tgInlineMenu.pagination_action_id()):
            
            settings_manager.set_setting( 
                self._pager_settings_name, 
                int(self.session.message.get_action_data())
            )

            state_id = self.id
      
        return state_id
    

    async def _read_items_from_db(
            self, 
            domain_type: domainObjectTypes, 
            filters: Filters = None,
            sorting: Sorting = None,
            page: int = 0
    ):

        datamapper = DatamapperFactory('local').get()
        scheme     = SchemeFactory('local').get(domain_type)
        paging     = Paging(page, self._page_size) if page > 0 else None

        total_count = await datamapper.count(scheme, filters=filters)
        items       = await datamapper.read(
                                scheme, 
                                filters=filters,
                                sorting=sorting, 
                                paging=paging
                            )
        
        return (items, total_count)
    
    async def _create_menu(self, 
                          items: list, 
                          total_items: int, 
                          page: int
    ) -> tgInlineMenu:

        buttons = {}
        row_index = 0
        buttons.setdefault(row_index, [])
        for item in items:
            button = tgButton(
                item.view(self._definitions), 
                self._action_id, 
                item.id
            )

            if( len(buttons[row_index]) >= self._count_buttons_in_row ):
                row_index += 1
                buttons.setdefault(row_index, [])

            buttons[row_index].append(button)

        menu = tgInlineMenu(self._menu_id)
        menu.set_buttons(buttons, 'inline' )
        menu.enable_pagination(page, total_items, self._page_size)
        menu.add_row_of_buttons([self._definitions.btnBack])

        return menu
    
    async def _get_menu_by_page(
            self,
            domain_type: domainObjectTypes, 
            filters: Filters = None,
            sorting: Sorting = None,
            page: int = 0

    ) -> tgInlineMenu:
        
        items, total_items = await self._read_items_from_db(
            domain_type, filters, sorting, page)
        
        return await self._create_menu(items, total_items, page)


class StateProcessorChooseUser(ItemChooser):

    def __init__(self, session, chain:dict) -> None:
        super().__init__(session, chain, processorsTypes.CHOOSE_USER)

        self._menu_id='MENU_UM'
        self._action_id='CHOOSE_USERS'
        self._title = self.definitions.strBtnManageUsers
        self._pager_settings_name='page_choose_user'
        
    def get_resetting_settings(self):
        
        resetting_settings = super().get_resetting_settings()
        resetting_settings[SPUserManagementHelper.setting_name_chosen_user()] = 0
        
        return resetting_settings
    
    def init(self):

        filters = Filters()
        sorting = Sorting()

        filters.new_filter(ConditionTypeEQ(), 'is_blocked', False)
        sorting.new_sorting('is_wait_confirmation', 'desc')
        sorting.new_sorting('full_name_ext')

        self._filters = filters
        self._sorting = sorting
        self._domain_object_type = domainObjectTypes.User


    async def _process_hook(self, action_id, settings_manager):
        
        state_id = None

        if(action_id == self._action_id):

            user_id = self.session.message.get_action_data()
            settings_manager.set_setting(
                SPUserManagementHelper.setting_name_chosen_user(), 
                user_id
            )
            state_id = self._chain['NEXT']

        return state_id

class StateProcessorChooseManager(ItemChooser):
    
    def __init__(self, session, chain:dict) -> None:
        super().__init__(session, chain, processorsTypes.CHOOSE_MANAGERS)

        self._menu_id = 'MENU_CHOOSE_MANAGERS'
        self._action_id = 'CHOOSE_MANAGERS'
        self._title = self.definitions.strChooseManager
        self._pager_settings_name = 'page_choose_manager'

    def get_resetting_settings(self):
        
        resetting_settings = super().get_resetting_settings()
        
        return resetting_settings

    def init(self):

        filters = Filters()
        sorting = Sorting()

        sorting.new_sorting('last_name', 'asc')
        filters.new_filter(ConditionTypeEQ(), 'is_blocked', False)

        self._filters = filters
        self._sorting = sorting
        self._domain_object_type = domainObjectTypes.UserBitrix
    
    async def _process_hook(self, action_id, settings_manager):

        state_id = None

        if(action_id == self._action_id):

            users_management = UserManagement(self.session.user)
            manager_id  = self.session.message.get_action_data(int)
            manager     = await users_management.read_bitrix_user_by_id(manager_id)
            
            setting_name = SPUserManagementHelper.setting_name_chosen_user()
            user_id  = settings_manager.get_setting(setting_name, 0, int)
            
            await users_management.read_by_id(user_id)
            user = users_management.user
            user.manager = manager
            await users_management.save()
            
            state_id = settings_manager.pop_last_state_from_history()

        return state_id
    

class StateProcessorChooseProjectFilter(ItemChooser):

    def __init__(self, session, chain:dict) -> None:
        super().__init__(session, chain, processorsTypes.LABOR_COST_REPORT_FILTER_PROJECT)

        self._menu_id='MENU_PROJECTS'
        self._action_id='CHOOSE_PROJECT'
        self._title = self.definitions.strProjectFilter
        self._pager_settings_name='page_choose_project'
        
    def get_resetting_settings(self):
        
        resetting_settings = super().get_resetting_settings()
        
        return resetting_settings
    
    def init(self):

        filters = Filters()
        sorting = Sorting()

        filters.new_filter(ConditionTypeEQ(), 'deleted', False)
        sorting.new_sorting('name', 'asc')
        
        self._filters = filters
        self._sorting = sorting
        self._domain_object_type = domainObjectTypes.Project

    async def _process_hook(self, action_id, settings_manager):
        
        state_id = None

        if(action_id == self._action_id):
            settings_manager = UserSettingsManager(self.session)
            project_id = self.session.message.get_action_data(int)
            settings_manager.set_setting('report_filter_project', project_id)
            state_id = settings_manager.pop_last_state_from_history()

        return state_id


class StateProcessorChooseEmployeeFilter(ItemChooser):

    def __init__(self, session, chain:dict) -> None:
        super().__init__(session, chain, processorsTypes.LABOR_COST_REPORT_FILTER_EMPLOYEE)

        self._menu_id='MENU_EMPLOYEE_CHOOSE'
        self._action_id='CHOOSE_EMPLOYEE'
        self._title = self.definitions.strEmployeeFilter
        self._pager_settings_name='page_choose_employee'
        
    def get_resetting_settings(self):
        
        resetting_settings = super().get_resetting_settings()
        return resetting_settings
    
    def init(self):

        filters = Filters()
        sorting = Sorting()

        sorting.new_sorting('last_name', 'asc')
        filters.new_filter(ConditionTypeEQ(), 'is_blocked', False)
        
        self._filters = filters
        self._sorting = sorting
        self._domain_object_type = domainObjectTypes.UserBitrix

    async def _process_hook(self, action_id, settings_manager):
        
        state_id = None

        if(action_id == self._action_id):
            settings_manager = UserSettingsManager(self.session)
            employee_id = self.session.message.get_action_data(int)
            settings_manager.set_setting('report_filter_employee', employee_id)
            state_id = settings_manager.pop_last_state_from_history()

        return state_id


