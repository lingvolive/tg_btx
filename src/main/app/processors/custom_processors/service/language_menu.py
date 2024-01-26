
from app.telegram_bot.bot_interface import (
    tgButton,
    tgInlineMenu
)

from app.resources.languages import Languages

class LanguageMenu():
  
    def __init__(self, definitions, menu_id, button_action_id, max_buttons_in_row):
       
       self._definitions = definitions
       self._max_buttons_in_row = max_buttons_in_row
       self._languages = Languages()
       self._button_action_id = button_action_id
       self._menu_id = menu_id

    def _create_button(self, language_item : dict, user_language_codes : list) -> tgButton:
        
        button = tgButton(
            language_item['name'], 
            self._button_action_id, 
            language_item['code']
        )

        if(language_item['code'] in user_language_codes):
            button.set_default()

        return button

    def _create_menu_buttons(self, language_codes : list, chosen_language_codes : list):
        
        buttons = {}
        button_row_idx      = 0
        added_button_in_row = 0
      
        for language_code in language_codes:
            
            language_item = self._languages.get_language_by_code(language_code)
            button  = self._create_button(language_item, chosen_language_codes)

            if added_button_in_row == self._max_buttons_in_row:
                added_button_in_row = 0
                button_row_idx    += 1

            buttons.setdefault(button_row_idx, [])

            buttons[button_row_idx].append(button)
            added_button_in_row += 1

        return buttons

    def create_menu(
            self, 
            language_codes : list, 
            chosen_language_codes, 
        ):

        if isinstance(chosen_language_codes, str):
            users_language_codes = [chosen_language_codes]
        else:
            users_language_codes = chosen_language_codes

        buttons = self._create_menu_buttons(language_codes, users_language_codes)
        menu = tgInlineMenu(self._menu_id)
        menu.set_buttons(buttons, 'inline' )
       
        return menu
