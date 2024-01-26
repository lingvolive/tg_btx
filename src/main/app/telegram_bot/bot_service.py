

from aiogram.utils.callback_data import CallbackData
from aiogram import types

class CallbackDataBuilder:
    """Class for creating callback data for inline keyboard buttons."""

    def __init__(self, prefix: str = 'InlineMenu', default_callback_params: list = ['menu_id', 'action_id', 'action_data']):
        """
        Initialize the CallbackData instance.

        :param prefix: The prefix of the callback data.
        :param default_callback_params: The default parameters to be included in the callback data.
        """
        self._prefix = prefix
        self._default_callback_params = default_callback_params

    def handler_filter(self):
        """Filter callback data based on the prefix and default parameters."""
        return CallbackData(self._prefix, *self._default_callback_params).filter()

    def new(self, menu_id, callback_params):
        """
        Create a new callback data.

        :param menu_id: The ID of the menu to which the callback data belongs.
        :param callback_params: The parameters to be included in the callback data.

        :return: The new callback data.
        """
        result_params_list = []
        result_params = {}

        result_params_list.append('menu_id')
        result_params['menu_id'] = menu_id

        for key in self._default_callback_params:
            value = callback_params.get(key)
            if value is not None:
                result_params_list.append(key)
                result_params[key] = value

        callback_data = CallbackData(self._prefix, *result_params_list)

        return callback_data.new(**result_params)



class InlineMenu():

    def __init__(self, menu_id, row_width = 1, use_paging=False, always_padding= False ) -> None:

        self._menu_id    = menu_id
        self._btns       = []
        self._use_paging = use_paging
        self._keyboard   = types.InlineKeyboardMarkup(row_width=row_width)
        self._always_padding = always_padding
        self._max_buttons_to_screen = 8
        

    def  add_button(self, caption: str, action_id: int, action_data : dict ):
        
        self._btns.append[ {'caption': caption, 'action_id': action_id, 'action_data': action_data} ]

    def _create_inline_btns(self, btns):

        call_back_data = CallbackDataBuilder()
    
        buttons = [ types.InlineKeyboardButton( text=btn['caption'],  
                                                callback_data=call_back_data.new( self._menu_id,  btn  ) 
                                               ) 
                for btn in btns  
        ]

        return buttons

    def _btns_to_show(self, page):

        if(self._use_paging and not self._always_padding):
            
            count_bottuns = len( self._btns )
            total_pages   = ( count_bottuns  + self._max_buttons_to_screen - 1 ) // self._max_buttons_to_screen 
            
            num_page = min(page, total_pages - 1)

            start_pos = self._max_buttons_to_screen * num_page
            end_pos   = self._max_buttons_to_screen * num_page + self._max_buttons_to_screen
            btns = self._btns[ start_pos : end_pos  ]

        else:
            btns = self._btns
            total_pages = 1

        return (btns, total_pages)

    def _create_paging_btns(self, page, total_page):

        if not self._use_paging:
            return

        btn_next = {'descr': '>>', 'action':df.MENU_ACTION_PAGE_NEXT, 'action_data':page} 
        btn_prev = {'descr': '<<', 'action':df.MENU_ACTION_PAGE_PREV, 'action_data':page}

        btns  = []

        if(page > 0 or self._always_padding):
            btns.append(btn_prev)
        
        if( page < total_page - 1 and total_page > 1 or self._always_padding):
            btns.append(btn_next)

        buttons = self._create_inline_btns( btns)

        self._keyboard.row( *buttons )


    def create(self, page = 0):

        btns, total_pages = self._btns_to_show(page)

        buttons = self._create_inline_btns( btns)
        
        self._keyboard.add( *buttons )

        self._create_paging_btns(page, total_pages)

        return self._keyboard

