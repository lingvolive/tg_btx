
from abc import ABC, abstractmethod

from app.processors.custom_processors.service.helpers import SPUserManagementHelper
from app.processors.custom_processors.service.user_management import UserManagement
from app.resources.enums import processorsTypes
from app.models.custom_models.session.user_settings_manager import UserSettingsManager
from app.processors.custom_processors.service.user_management import UserManagement
from app.resources.enums import tgMessageTypes
from app.telegram_bot.bot_message import tgUserMassage
from app.processors.tasks.task import Task
from app.processors.custom_processors.service.labor_cost_report import LaborCostReport
from app.resources.resource_definitions import ResourceDefinition

class TaskGenerateLaborCostReport(Task):

    def __init__(self, params: dict) -> None:
        super().__init__(params)
        self._report_settings = params['settings']
        self._message_id = params['message_id']
        self._user_id = params['user_id']
        self._bot = params['bot']
        
    async def process(self, state_processor_manager_cls):

        user_management = UserManagement()
        user = await user_management.read_by_id(self._user_id, read_session=True)
        session = user_management.session

        message = tgUserMassage(
                message_type = tgMessageTypes.TEXT,
                message={
                      'bot':self._bot, 
                      'chat_id':self._user_id,
                      'message_id': self._message_id,
                      'user' : user
                    }
        )

        
        session.message = message

        app_resources = ResourceDefinition(user.language)
        report = LaborCostReport(session, app_resources, self._report_settings)
        report_file = await report.generate_report()

        user_settings_manager = UserSettingsManager(session)
        #user_settings_manager.push_state_to_history(session.state_id)
        
        user_settings_manager.set_setting('report_file', report_file)

        await message.delete_message()

        await self.pre_process(
                processorsTypes.LABOR_COST_REPORT_READY, 
                user_management, state_processor_manager_cls
            )
        
        return
    


