

from app.resources.enums import processorsTypes
from app.processors.state_processor import StateProcessor

class StateProcessorNotImplemented(StateProcessor):

    def __init__(self, session, chain:dict) -> None:
        
        super().__init__(session, chain, processorsTypes.NOT_IMPLEMENTED)

    def get_resetting_settings(self):
        return {}

    async def pre_process(self) -> processorsTypes:
       
        await self.session.message.send(self.definitions.strNotImpelment, self.definitions.mNotImplementedMenu)

        return self.id
 
    async def process(self) -> processorsTypes:
        return await self._default_inline_keyboard_handler(self.definitions.mNotImplementedMenu)
      

        