

from app.resources.enums import processorsTypes
from app.processors.state_processor import StateProcessor


class StateProcessorSettings(StateProcessor):

    def __init__(self, session, chain:dict) -> None:
        
        super().__init__(session, chain, processorsTypes.SETTINGS)

    def get_resetting_settings(self):
        return {}

    async def pre_process(self) -> processorsTypes:
        
      
        main_menu    = self.definitions.mSettingsMenu
        text_message = self.definitions.strSettingsBtn
        
        await self.session.message.send(text_message, main_menu)

        return self.id
 
    async def process(self) -> processorsTypes:

        return await self._default_inline_keyboard_handler(self.definitions.mSettingsMenu)

       
   

       



  

        

        