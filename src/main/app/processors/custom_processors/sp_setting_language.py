

from app.resources.enums import processorsTypes
from app.processors.state_processor import StateProcessor
from app.telegram_bot.bot_interface import tgInlineMenu, tgButton

class StateProcessorSettingsLanguage(StateProcessor):

    def __init__(self, session, chain:dict) -> None:
        
        super().__init__(session, chain, processorsTypes.SETTINGS_LANGUAGE)

        self._menu_id = 'MENU_SET_LANG'
        self._action_id = 'CHOOSE_LANG'

    def get_resetting_settings(self):
        return {}

    async def pre_process(self) -> processorsTypes:
        
        df = self.definitions
        text_message = df.strSettingsLanguage

        languages = df.supported_languages

        buttons = {}
        button_row_idx      = 0
        added_button_in_row = 0
        max_buttons_in_row  = 2

        for language_id, language_view in languages.items():

            button = tgButton(language_view, self._action_id, language_id)

            if(language_id == self.session.user.language):
                button.set_default()

            if added_button_in_row == max_buttons_in_row:
                added_button_in_row = 0
                button_row_idx = button_row_idx + 1


            if button_row_idx not in buttons:
                buttons[button_row_idx] = []

            buttons[button_row_idx].append(button)
            added_button_in_row = added_button_in_row + 1


        buttons[button_row_idx + 1] = [df.btnBack]
        menu = tgInlineMenu(self._menu_id)
        menu.set_buttons(buttons, 'inline')
 
        await self.session.message.send(text_message, menu)

        return self.id
 
    async def process(self) -> processorsTypes:

        state_id =  await self._default_inline_keyboard_handler()

        if( not state_id == self.id ):
            return state_id

        if(self.session.message.is_inline() and self._menu_id == self.session.message.get_menu_id()):

            action_id = self.session.message.get_action_id()

            if(action_id == self._action_id):

                action_data = self.session.message.get_action_data()
                self.session.user.language = action_data
                state_id = self.id

            if(action_id == tgInlineMenu.pagination_action_id()):
                self.session.data['page'] = int(self.session.message.get_action_data())
                state_id = self.id
      
        return state_id

       
   

       



  

        

        