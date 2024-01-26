

from app.resources.enums import processorsTypes
from app.processors.state_processor import StateProcessor


class StateProcessorCommandStart(StateProcessor):

    def __init__(self, session, chain:dict) -> None:
        
        super().__init__(session, chain, processorsTypes.COMMAND_START)

    def get_resetting_settings(self):
        return {}

    async def pre_process(self) -> processorsTypes:
        return self._chain.get( 'NEXT' )
 
    async def process(self) -> processorsTypes:

        return self._chain.get( 'NEXT' )
    
class StateProcessorCommandAdmin(StateProcessor):

    def __init__(self, session, chain:dict) -> None:
        
        super().__init__(session, chain, processorsTypes.COMMAND_START)

    def get_resetting_settings(self):
        return {}

    async def pre_process(self) -> processorsTypes:
        return self._chain.get( 'NEXT' )
 
    async def process(self) -> processorsTypes:

        return self._chain.get( 'NEXT' )
    
    
        

        