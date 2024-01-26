#from typing import Annotated
from abc import ABC, abstractmethod
from app.resources.enums import processorsTypes
from app.resources.resource_definitions import ResourceDefinition
from app.models.custom_models.session.user_settings_manager import UserSettingsManager


class StateProcessor(ABC):

    def __init__(self, session, chain:dict, state_id : processorsTypes) -> None:
        super().__init__()

        self._session  = session
        self._id       = state_id #: Annotated[int    , 'id']      = state_id
        self._chain    = chain #: Annotated[dict    , 'Sequence of actions']  = chain
        self._definitions = ResourceDefinition(self.session.user.language)

    @property
    def session(self):
        return self._session

    @property
    def id(self):
        return self._id

    @property
    def definitions(self):
        return self._definitions

    def get_chain(self):
        return self._chain

    def get_step_from_chain(self, step_name:str):
        return self._chain[step_name]

    async def _default_inline_keyboard_handler(self, menu = None):

        message  = self.session.message
        settings_manager = UserSettingsManager(self.session)
      
        if( not message.is_inline()):
            return self._id

        if( menu is not None and not menu == message.get_menu_id() ):
            return self.id

        pressed_button = message.get_action_id()

        if(pressed_button == self.definitions.btnBack):
            return settings_manager.pop_last_state_from_history()

        next_state_id = self._chain.get( pressed_button)
        if(next_state_id is not None):
            settings_manager.push_state_to_history(self.id)
        else:
            next_state_id = self.id
        
        return next_state_id

    @abstractmethod
    async def pre_process(self) -> processorsTypes:
        pass

    @abstractmethod
    async def process(self) -> processorsTypes:
        pass

    @abstractmethod
    def get_resetting_settings(self):
        return {}




