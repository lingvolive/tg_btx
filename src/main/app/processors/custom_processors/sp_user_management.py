from abc import ABC, abstractmethod

from app.resources.enums import processorsTypes
from app.processors.state_processor import StateProcessor
from app.processors.custom_processors.service.helpers import SPUserManagementHelper
from app.processors.custom_processors.service.user_management import UserManagement
from app.models.custom_models.session.user_settings_manager import UserSettingsManager
from app.models.custom_models.user.role import Role
from app.processors.tasks.events_manager import EventsManager, eventTypes

from app.telegram_bot.bot_interface import (
    tgButton,
    tgInlineMenu
)

class StateProcessorUserManagement(StateProcessor, ABC):

    def __init__(self, session, chain: dict, state_id: processorsTypes) -> None:
        super().__init__(session, chain, state_id)

        self._user_settings = UserSettingsManager(session)
        self._user_management = UserManagement(self.session.user)

    def _get_edited_user_id(self):

        user_id = self._user_settings.get_setting(
            SPUserManagementHelper.setting_name_chosen_user(), 
            0
        )
        return int(user_id)

    @abstractmethod
    async def pre_process(self):
        pass

    @abstractmethod
    async def process(self):
        pass

class StateProcessorUserManagementMenu(StateProcessorUserManagement):

    def __init__(self, session, chain:dict ):
        super().__init__(session, chain, processorsTypes.USER_MANAGE) 

        self._menu = self.definitions.mUserManageMenu
    
    def get_resetting_settings(self):
        return {}

    async def pre_process(self):

        user_id = self._get_edited_user_id()
        await self._user_management.read_by_id(user_id)
        user = self._user_management.user
        
        await self.session.message.send(
            SPUserManagementHelper.user_profile_menu_text(user, self.definitions),
            SPUserManagementHelper.user_management_menu(self.definitions)
        )
        
        return self.id
   
    async def process(self):

        state_id = await self._default_inline_keyboard_handler()

        if( not state_id == self.id ):
            return state_id

        if( not self.session.message.is_inline() or 
           not self._menu == self.session.message.get_menu_id()
        ):
            return state_id

        user_id = self._get_edited_user_id()
        action_id = self.session.message.get_action_id()

        if(action_id == self.definitions.btnBlockUser):
            await self._user_management.read_by_id(user_id)
            self._user_management.block()
            await self._user_management.save()
            state_id = self._user_settings.pop_last_state_from_history()
        
        return state_id

class StateProcessorUserManagementSetRoles(StateProcessorUserManagement):

    def __init__(self, session, chain:dict ):
        super().__init__(session, chain, processorsTypes.USER_MANAGE_SET_ROLES) 

        self._menu_id = 'SET_ROLES_MENU'
        self._action_id = 'CHOOSE_ROLE'
        
    def get_resetting_settings(self):
        return {}

    async def pre_process(self):

        user_id = self._get_edited_user_id()
        user = await self._user_management.read_by_id(user_id)
         
        buttons = {}
        btn_idx = 0
        for role_name, role_descr in Role.get_roles(self.definitions).items():

            button = tgButton(role_descr, self._action_id, role_name)

            if(user.has_role(role_name)):
                button.set_default()

            buttons[btn_idx] = [button]
            btn_idx += 1

        menu = tgInlineMenu(self._menu_id)
        menu.set_buttons(buttons, 'inline' )
        menu.add_row_of_buttons([self._definitions.btnBack])

        await self.session.message.send(
            SPUserManagementHelper.user_profile_menu_text(user, self.definitions),
            menu
        )
        
        return self.id
   
    async def process(self):

        state_id = await self._default_inline_keyboard_handler()

        if( not state_id == self.id ):
            return state_id

        if( not self.session.message.is_inline() or 
           not self._menu_id == self.session.message.get_menu_id()
        ):
            return state_id

        user_id = self._get_edited_user_id()
        action_id = self.session.message.get_action_id()

        if(action_id == self._action_id):

            await self._user_management.read_by_id(user_id)
            user = self._user_management.user
            role_name     = self.session.message.get_action_data()
            start_numbers_roles = len(user.roles)

            if(user.has_role(role_name)):
                self._user_management.delete_role(user, role_name)
            else:
                self._user_management.add_role(user, role_name)

            await self._user_management.save()
            state_id = self.id

            if(start_numbers_roles == 0 and len(user.roles) > 0):
                await self._notify_user_registered(user_id)
        
        return state_id
    
    async def _notify_user_registered(self, user_id):

        task_params = {
                'user_id': user_id,
                'bot': self.session.message.bot
            }
        
        event_manager = EventsManager()
        await event_manager.notify(eventTypes.USER_REGISTERED, task_params)
            
        



