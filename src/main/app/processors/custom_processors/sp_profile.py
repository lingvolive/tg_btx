
from abc import ABC, abstractmethod

from app.resources.enums import processorsTypes
from app.processors.state_processor import StateProcessor
from app.processors.custom_processors.service.user_management import UserManagement
from app.processors.tasks.events_manager import EventsManager, eventTypes
from app.config.config import Config


class StateProcessorProfile(StateProcessor, ABC):

    def __init__(self, session, chain:dict, processor_type:processorsTypes ) -> None:

        super().__init__(session, chain, processor_type)
        self._title = ''
        self._enter_text = ''
        self._user = session.user
    
    @abstractmethod
    async def process_extend(self):
        pass

    @abstractmethod
    async def pre_process_extend(self):
        return self.id

    def get_resetting_settings(self):
        return {}

    async def pre_process(self) -> processorsTypes:
       
        profile_text  = self._user.profile_text(self.definitions)
        message_text = f'*{self.definitions.strProfile}*\n'\
                       f'{profile_text}'\
                       f'\n\n*{self._enter_text}*'
        
        await self.session.message.send(message_text)
       
        return await self.pre_process_extend()
 
    async def process(self) -> processorsTypes:

         if not self.session.message.is_text():
            return self.id
         
         return await self.process_extend()
   
        
class StateProcessorProfileView(StateProcessorProfile):

    def __init__(self, session, chain:dict ):
        super().__init__(session, chain, processorsTypes.PROFILE_VIEW) 

        self._menu = self.definitions.mProfileViewMenu

    async def pre_process(self):

        profile_text  = self._user.profile_text(self.definitions)
        message_text = f'*{self.definitions.strProfile}*\n'\
                       f'{profile_text}'
        
        await self.session.message.send(message_text, self._menu)
       
        return self.id
    
    async def pre_process_extend(self):
        return self.id

    async def process(self):
        return await self._default_inline_keyboard_handler(self._menu)
    
    async def process_extend():
        pass
        
class StateProcessorLoginEmail(StateProcessorProfile):

    def __init__(self, session, chain:dict ):
        super().__init__(session, chain, processorsTypes.LOGIN_INPUT_EMAIL) 

        self._enter_text = self.definitions.strEnterEmail

    async def pre_process_extend(self):
        return self.id
     
    async def process_extend(self):

        self.session.user.email = self.session.message.get_text()

        return self._chain['NEXT']
    
class StateProcessorLoginFullName(StateProcessorProfile):

    def __init__(self, session, chain:dict ):
        super().__init__(session, chain, processorsTypes.LOGIN_INPUT_FULL_NAME) 

        self._enter_text = self.definitions.strEnterName

    async def pre_process_extend(self):
        return self.id
    
    async def process_extend(self):

        self.session.user.full_name_ext = self.session.message.get_text()

        return self._chain['NEXT']
    
class StateProcessorLoginPhone(StateProcessorProfile):

    def __init__(self, session, chain:dict ):
        super().__init__(session, chain, processorsTypes.LOGIN_INPUT_PHONE) 

        self._enter_text = self.definitions.strEnterPhone

    async def pre_process_extend(self):
        return self.id
    
    async def process_extend(self):

        self.session.user.phone_ext = self.session.message.get_text()

        return self._chain['NEXT']
    
class StateProcessorLoginWaitConfirmation(StateProcessorProfile):

    def __init__(self, session, chain:dict ):
        super().__init__(session, chain, processorsTypes.LOGIN_WAIT_CONFIRMATION) 

        self._enter_text = self.definitions.strWaitConfirmation
        
    async def pre_process_extend(self):

        self.session.user.is_wait_confirmation = True

        task_params = {
            'user_id': self.session.user.id,
            'bot': self.session.message.bot
        }

        even_manager = EventsManager()
        await even_manager.notify(eventTypes.NEW_USER, task_params)
        
        return self.id
    
    async def process_extend(self):
        return self.id

class StateProcessorSetAdmin(StateProcessor):

    def __init__(self, session, chain:dict) -> None:
        super().__init__(session, chain, processorsTypes.SET_ADMIN)

    def get_resetting_settings(self):
        return {}

    async def pre_process(self) -> processorsTypes:
        return self.id

    async def process(self) -> processorsTypes:

        if not self.session.message.is_text():
            return self.id
        
        config = Config() 
        password = self.session.message.get_text()

        if password == config.tg_bot.admin_password:
            await self._set_admin_role()
            await self.session.message.send(
                self.definitions.strAdminRightGranted
            )
        
        return self._chain.get( 'NEXT' )

    async def _set_admin_role(self):

        users_management = UserManagement(self.session.user)
        users_management.add_role(self.session.user, 'admin')
        users_management.add_role(self.session.user, 'employee')



    

            
    
    

