

from app.resources.enums import processorsTypes
from app.processors.state_processor import StateProcessor



class StateProcessorMainMenu(StateProcessor):

    def __init__(self, session, chain:dict) -> None:
        
        super().__init__(session, chain, processorsTypes.MAIN)

    def get_resetting_settings(self):
        return {'steps_history':[]}
    
    async def pre_process(self) -> processorsTypes:
        
        main_menu = self.definitions.mMainMenu
        
        await self.session.message.send(self.definitions.strMainMenu, main_menu)
 
        return self.id
 
    async def process(self) -> processorsTypes:
        
       return await self._default_inline_keyboard_handler(self.definitions.mMainMenu)

        

       
        

        