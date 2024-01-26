from app.resources.enums import processorsTypes
from app.processors.state_processor import StateProcessor

class StateProcessorNone(StateProcessor):

    def __init__(self, session, chain:dict) -> None:
        
        super().__init__(session, chain, processorsTypes.NONE)

    def get_resetting_settings(self):
        return {}

    async def pre_process(self) -> processorsTypes:
        
        if(self.session.user.is_auth):
            return self._chain['AUTH_USER']
        else:
            return self._chain['LOGIN_INPUT_EMAIL']

 
    async def process(self) -> processorsTypes:

        if(self.session.user.is_auth):
            return self._chain['AUTH_USER']
        else:
            return self._chain['LOGIN_INPUT_EMAIL']
        