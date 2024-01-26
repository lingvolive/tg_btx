from enum import Enum, auto
from aiogram import types

from app.telegram_bot.bot_service import CallbackDataBuilder

class ButtonAppearanceType(Enum):
    NONE = auto
    DEFAULT = auto()
    CHECKED = auto()
    ARROW_BACK = auto()
    DOUBLE_ARROW_BACK = auto()
    ARROW_FORWARD = auto()
    DOUBLE_ARROW_FORWARD = auto()


class tgButton():

    def __init__(self, caption, action_id, action_data, roles=[]):

        self._action_id   = action_id
        self._caption     = caption
        self._action_data = action_data
        self._is_enable    = True
        self._appearance_type = ButtonAppearanceType.NONE
        self._roles = roles

        self._appearance_image_map = {
            ButtonAppearanceType.NONE : {'prefix':'', 'suffix':''},
            ButtonAppearanceType.DEFAULT : {'prefix':'∙ ', 'suffix':' ∙'},
            ButtonAppearanceType.CHECKED : {'prefix':'✔', 'suffix':''},
            ButtonAppearanceType.ARROW_BACK : {'prefix':'<', 'suffix':''},
            ButtonAppearanceType.DOUBLE_ARROW_BACK : {'prefix':'≪', 'suffix':''},
            ButtonAppearanceType.ARROW_FORWARD : {'prefix':'', 'suffix':'>'},
            ButtonAppearanceType.DOUBLE_ARROW_FORWARD : {'prefix':'', 'suffix':'≫'},
        }
        
   
    @property
    def action_id(self):
        return self._action_id

    @property
    def caption(self):

        prefix = self._appearance_image_map[ self._appearance_type ]['prefix']
        suffix = self._appearance_image_map[ self._appearance_type ]['suffix']

        return f'{prefix}{self._caption}{suffix}'

    @property
    def action_data(self):
        return self._action_data

    @action_data.setter
    def action_data(self, action_data : dict):
        self._action_data = action_data

    @property
    def roles(self):
        return self._roles

    @roles.setter
    def roles(self, roles):
        self._roles = roles

    def __eq__(self, other):

        if(isinstance(other, str)):
            return self.action_id == other

        return self.action_id == other.action_id

    def __hash__(self):
        return hash( self.action_id)

    def enable(self):
        self._is_enable = True
    
    def disable(self):
        self._is_enable = False

    def is_enable(self):
        return self._is_enable
    
    def has_access(self, user):

        if(user is None):
            return False
        
        if(len(self.roles) == 0):
            return True

        has_access = False

        for role in self.roles:
            has_access = user.has_role(role)
            if(has_access):
                break
        
        return has_access
        
        
    def set_default(self):
        self._appearance_type = ButtonAppearanceType.DEFAULT
    
    def set_check(self):
        self._appearance_type = ButtonAppearanceType.CHECKED

    def set_arrow_back(self):
        self._appearance_type = ButtonAppearanceType.ARROW_BACK

    def set_double_arrow_back(self):
        self._appearance_type = ButtonAppearanceType.DOUBLE_ARROW_BACK

    def set_arrow_forward(self):
        self._appearance_type = ButtonAppearanceType.ARROW_FORWARD

    def set_double_arrow_forward(self):
        self._appearance_type = ButtonAppearanceType.DOUBLE_ARROW_FORWARD

    def reset_appearance_properties(self):

        self._appearance_type = ButtonAppearanceType.NONE

    def _create_button_inline(self, menu_id):

        callback = CallbackDataBuilder()
        callback_data = { 
            'caption':self.caption, 
            'action_id':self.action_id, 'action_data':self.action_data 
        }
    
        return types.InlineKeyboardButton( 
            text=self.caption,  
            callback_data=callback.new( menu_id,  callback_data ) 
            ) 

    def _create_button(self, menu_id):
       
        return types.KeyboardButton(self.caption) 
            

    def create_button(self, menu_id, keyboard_type):

        if(keyboard_type == 'inline'):
            return self._create_button_inline(menu_id)
        else:
            return self._create_button(menu_id)
 
class tgPaginationBuilder():

    def __init__(self, items_per_page = 20, max_pagination_buttons = 6):
        
        self._max_pagination_buttons = max_pagination_buttons
        self._items_per_page = items_per_page
        
    @staticmethod
    def pagination_action_id():

        return 'PAGINATION'
   
    def create_pagination_buttons(self, page, total_items):

        pagination_buttons = []
        first_page  = 1
        last_page   = ( total_items + self._items_per_page - 1 ) // self._items_per_page 

        if(first_page == last_page):
            return pagination_buttons
        
        button_indexes = self._get_button_indexes(first_page, last_page, page)

        for button_index_item in button_indexes:

            button = tgButton( 
                f'{button_index_item}', 
                self.pagination_action_id(), 
                button_index_item  
            )

            if(page == button_index_item):
                button.set_default()

            elif( button_index_item == first_page and not self._is_index_consecutive(button_indexes)):
                button.set_double_arrow_back()

            elif( button_index_item == last_page and not self._is_index_reverse_consecutive(button_indexes) ):
                button.set_double_arrow_forward()

            elif( button_index_item == button_indexes[1] and not self._is_index_consecutive(button_indexes) ):
                button.set_arrow_back()

            elif( button_index_item == button_indexes[-2] and not self._is_index_reverse_consecutive(button_indexes) ):
                button.set_arrow_forward()

            pagination_buttons.append(button)

        return pagination_buttons
    
    def _get_button_indexes(self, first_page, last_page, page):

        button_indexes = [first_page, last_page]

        if(not page in button_indexes ):
            button_indexes.insert(1, page)

        add_to_left = not page == first_page
            
        while len(button_indexes) < self._max_pagination_buttons:

            is_index_consecutive          = self._is_index_consecutive(button_indexes)
            is_index_reverse_consecutive  = self._is_index_reverse_consecutive(button_indexes)

            if(is_index_consecutive and is_index_reverse_consecutive):
                break
            elif(is_index_consecutive):
                add_to_left = False
            elif(is_index_reverse_consecutive):
                add_to_left = True

            if(add_to_left):
                self._add_index_to_left_edge(button_indexes)
                add_to_left = False
            else:
                self._add_button_to_right_edge(button_indexes)
                add_to_left = True

        return button_indexes

    @staticmethod
    def _add_index_to_left_edge(button_indexes):
        button_indexes.insert(1, button_indexes[1] - 1)

    @staticmethod
    def _add_button_to_right_edge(button_indexes):
        button_indexes.insert(-1, button_indexes[-2] + 1)

    @staticmethod
    def _is_index_consecutive(button_indexes):
        return button_indexes[0] + 1 == button_indexes[1]
    
    @staticmethod
    def _is_index_reverse_consecutive(button_indexes):
        return button_indexes[-1] - 1 == button_indexes[-2]
            
class tgInlineMenu():

    def __init__(self, menu_id) -> None:

        self._menu_id = menu_id
        self._rows_of_buttons = {}
        self._rows_of_buttons_inline = {}
        self._enable_pagination = False
        self._page  = 0
        self._items_per_page     = 0
        self._total_items        = 0

    @staticmethod
    def pagination_action_id():

        return tgPaginationBuilder.pagination_action_id()
      
    def set_buttons(self, rows_of_buttons: dict, menu_type = 'inline') -> None:

        if(menu_type == 'inline'):
            self._rows_of_buttons_inline = rows_of_buttons
        else:
            self._rows_of_buttons = rows_of_buttons
        
    def add_row_of_buttons(
            self, 
            buttons: list,
            position = -1,
            menu_type = 'inline'
    ):
        menu_type_attr_button_map = {
            'inline': '_rows_of_buttons_inline',
            'keyboard': '_rows_of_buttons'
        }
        
        rows_of_buttons = getattr(self,menu_type_attr_button_map[menu_type] )
        
        if(len(rows_of_buttons) == 0):
            position_for_inserting = 0
            last_position = -1
        else:
            last_position = max(rows_of_buttons.keys())

        if(position > last_position or position == -1):
            position_for_inserting = last_position + 1
        else:
            position_for_inserting = position
        
        new_rows_of_buttons = {}
        for k,v in rows_of_buttons.items():
            if(k >= position_for_inserting):
                k += 1
            new_rows_of_buttons[k] = v

        new_rows_of_buttons[position_for_inserting] = buttons
        setattr(self, menu_type_attr_button_map[menu_type], new_rows_of_buttons )
       
    def enable_pagination(self, page : int, 
                          total_items : int, items_per_page : int = 10):
        
        self._page = page
        self._enable_pagination = True
        self._total_items       = total_items
        self._items_per_page    = items_per_page

        if(total_items == 0):
            return

        pagination_builder = tgPaginationBuilder(self._items_per_page)

        buttons = pagination_builder.create_pagination_buttons(
            self._page, 
            self._total_items
        )

        self.add_row_of_buttons(buttons)

    def create(self, user):

        inline_keyboard = self.create_keyboard(
            self._rows_of_buttons_inline, 
            'inline',
            user
        
        )
        keyboard        = self.create_keyboard(
            self._rows_of_buttons, 
            'keyboard',
            user
        )

        empty_keyboards = self.get_empty()

        keyboards = {}

        if len(inline_keyboard.inline_keyboard) == 0:
            keyboards['inline'] = empty_keyboards['inline']
        else:
            keyboards['inline'] = inline_keyboard

        if len(keyboard.keyboard) == 0:
            keyboards['keyboard'] = empty_keyboards['keyboard']
        else:
            keyboards['keyboard'] = types.ReplyKeyboardRemove()

        return keyboards

    def create_keyboard(self, rows_of_buttons, keyboard_type, user):

        if(keyboard_type == 'inline'):
            keyboard = types.InlineKeyboardMarkup()
        else:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

        button_keys = sorted(rows_of_buttons.keys())

        for number_row_of_button in button_keys:
            
            row_of_buttons = [ button.create_button(self._menu_id, keyboard_type) 
                                for button in rows_of_buttons[number_row_of_button]
                                if button.has_access(user)
            ]
          
            keyboard.row( *row_of_buttons )

         #if(keyboard_type=='inline' and self._enable_pagination):
         #   self._add_pagination_keyboard(keyboard)

        return keyboard
    
    def _add_pagination_keyboard(self, keyboard):

        row_of_buttons   = []
        
        pagination_builder = tgPaginationBuilder(self._items_per_page)

        buttons = pagination_builder.create_pagination_buttons(
            self._page, 
            self._total_items
        )

        row_of_buttons = [ button.create_button( self._menu_id, 'inline' ) 
                          for button in buttons 
                        ]
       
        if len(row_of_buttons) > 0:
            keyboard.row(*row_of_buttons)
      
    @staticmethod
    def get_empty():
       
        return {
            'keyboard': types.ReplyKeyboardRemove(), 
            'inline': types.InlineKeyboardMarkup() 
        }
   
    def __eq__(self, other):

        if( isinstance(other, str) ):
            return self._menu_id == other

        return self._menu_id == other._menu_id

 
       









        
        


