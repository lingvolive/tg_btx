

from app.resources.enums import processorsTypes
from app.processors.state_processor import StateProcessor

class State_processor_help(StateProcessor):

    def __init__(self, session, chain:dict) -> None:
        
        super().__init__(session, chain, processorsTypes.HELP)

    def get_resetting_settings(self):
        return {}

    async def pre_process(self) -> processorsTypes:
       
        await self.session.message.send(self.definitions.strHelp, self.definitions.mHelpMenu)
       
        return self.id
 
    async def process(self) -> processorsTypes:

        return await self._default_inline_keyboard_handler(self.definitions.mHelpMenu)