import os
from app.telegram_bot.bot_message_base import tgMessageBase
from typing import Union
from aiogram.types import Message, CallbackQuery
from aiogram.types import Message



from app.telegram_bot.bot_interface import tgInlineMenu
from app.resources.enums import tgMessageTypes


class tgUserMassage(tgMessageBase):

    def __init__(
            self, 
            message_type: tgMessageTypes, 
            message: Union[Message, CallbackQuery], 
            callback_data : dict = {},
            params : dict = {}
        ) -> None:

        super().__init__(message_type, message, callback_data, params)

    @property
    def tg_message(self):
        return self._message
    
    def user_info(self):

        user_info_struct = ['id', 'first_name', 'last_name', 
                            'full_name', 'is_bot', 'username', 
                            'language_code', 'url',
        ]

        user_info = { user_attr: getattr(self._from_user, user_attr) 
                      for user_attr in  user_info_struct 
                    }

        return user_info
    
    async def send(self, message_text: str, menu: tgInlineMenu = None):

        keyboards = tgInlineMenu.get_empty() if menu is None else menu.create(self.user)

        if( self.is_inline() 
           and self.message_id is not None
           and self.content_type == 'text'
        ):
            await self.answer_callback_query()
            message = await self._bot.edit_message_text(
                text         = message_text,
                chat_id      = self.chat_id,
                message_id   = self.message_id,
                reply_markup = keyboards['inline'],
                parse_mode   = 'Markdown'  

            )
            
        else:
             message = await self._bot.send_message(
                chat_id=self.chat_id,
                text= message_text,
                reply_markup=keyboards['inline'],
                parse_mode='Markdown' 
                
            )
             
        if(self.session_log is not None):
            self.session_log.finish_log(message_text)

        return message
 
    async def reply(self, message_text: str, menu: tgInlineMenu = None):

        keyboards = tgInlineMenu.get_empty() if menu is None else menu.create(self.user)

        message = await self._bot.send_message(
            chat_id= self.chat_id,
            text = message_text,
            reply_to_message_id = self.message_id,
            reply_markup=keyboards['inline'],
            parse_mode='Markdown'
        )
        
        if(self.session_log is not None):
            self.session_log.finish_log(message_text)

        return message

    async def update_menu(self, menu):
        
        await self.answer_callback_query()
        await self._message.edit_reply_markup(reply_markup=menu.create(self.user)['inline'])

    async def answer_callback_query(self):

        if(self._callback_query is not None):
            await self._bot.answer_callback_query(self._callback_query.id)

    async def send_file(self, file_name :str, message_text: str, menu: tgInlineMenu = None):

        keyboards = tgInlineMenu.get_empty() if menu is None else menu.create(self.user)

        with open(file_name, "rb") as file:
            await self._bot.send_document(self._chat_id,
                                            file, 
                                            caption = message_text, 
                                            reply_markup=keyboards['inline'],
                                            parse_mode='Markdown')


        os.remove(file_name)

    async def delete_message(self):

        #from aiogram  import Bot

        if(self.message_id is not None):

            try:
                await self._bot.delete_message(chat_id=self._chat_id, 
                                           message_id=self.message_id)
            except Exception as err:
                pass
            
            self._message_id = None

        
    


