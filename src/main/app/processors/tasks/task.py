
from abc import ABC, abstractmethod

from app.processors.custom_processors.service.helpers import SPUserManagementHelper
from app.processors.custom_processors.service.user_management import UserManagement
from app.resources.enums import processorsTypes
from app.models.custom_models.session.user_settings_manager import UserSettingsManager
from app.processors.custom_processors.service.user_management import UserManagement
from app.resources.enums import tgMessageTypes
from app.telegram_bot.bot_message import tgUserMassage

class Task(ABC):

    def __init__(self, params: dict) -> None:
        super().__init__()

        self._params = params
        
    @abstractmethod
    async def process(self, state_processor_manager_cls):
        pass

    async def pre_process(
            self, state_id, 
            user_management, 
            state_processor_manager_cls):

        session = user_management.session

        state_processor = state_processor_manager_cls(session)
        processor = state_processor.get_processor(session, state_id)

        prev_state_id = state_id
        next_state_id = await processor.pre_process()

        while not prev_state_id == next_state_id:
            prev_state_id = next_state_id
            processor = state_processor.get_processor(session, next_state_id)

            next_state_id = await processor.pre_process()

        session.state_id = next_state_id
        await user_management.save()


class TaskNotifyEventNewUser(Task):

    def __init__(self, params: dict) -> None:
        super().__init__(params)
        self._user_id = params['user_id']
        self._bot = params['bot']
        
    async def process(self, state_processor_manager_cls):

        user_management = UserManagement()
        
        admin_roles = await user_management.read_roles_by_name('admin')
        user = await user_management.read_by_id(self._user_id)
       
        for admin_role in admin_roles:

            admin_user = await user_management.read_by_id(admin_role.user_id, read_session=True)
            session = user_management.session
            
            session.message = tgUserMassage(
                message_type = tgMessageTypes.TEXT,
                message={'bot':self._bot, 'chat_id':admin_user.id, 'user':session.user}
            )

            user_settings_manager = UserSettingsManager(session)
            user_settings_manager.push_state_to_history(session.state_id)
            user_settings_manager.set_setting(
                SPUserManagementHelper.setting_name_chosen_user(),
                user.id
            )

            await self.pre_process(
                processorsTypes.USER_MANAGE, 
                user_management,state_processor_manager_cls
            )
        
        return
    

class TaskNotifyEventUserRegistered(Task):

    def __init__(self, params: dict) -> None:
        super().__init__(params)
        self._user_id = params['user_id']
        self._bot = params['bot']
        
    async def process(self, state_processor_manager_cls):

        user_management = UserManagement()
        user = await user_management.read_by_id(self._user_id, read_session=True)
        session = user_management.session
        

        session.message = tgUserMassage(
                message_type = tgMessageTypes.TEXT,
                message={'bot':self._bot, 'chat_id':self._user_id, 'user': user}
        )
        
        
        await self.pre_process(processorsTypes.NONE, 
                               user_management,state_processor_manager_cls)

        return
    


    

