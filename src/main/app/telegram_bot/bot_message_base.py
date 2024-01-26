
import os

from typing import Union
from aiogram.types import Message, CallbackQuery
from abc import ABC, abstractmethod
from app.resources.enums import tgMessageTypes

from app.config.config import Config
from app.telegram_bot.bot_utils import tgUtils

class tgMessageBase(ABC):

    def __init__(
            self, 
            message_type: tgMessageTypes, 
            received_data: Union[Message, CallbackQuery, dict], 
            callback_data : dict = {},
            params: dict = {}
        ) -> None:

        self._user = None
        self._message_type = message_type
        self._file_id = None
        self._bot     = None
        self._chat_id = None
        self._message_id = None
        self._from_user  = None
        self._callback_data = None
        self._file      = None
        self._message_link = None
        self._content_type = None
        
        self._executer     = params.get('executer')
        self._task_queue   = params.get('task_queue')
        self._session_log  = None

        if( isinstance(received_data, dict)):
            self._init_message_from_dict(received_data)
        elif( isinstance(received_data, CallbackQuery) ):
            self._init_message(received_data.message, received_data, callback_data)
        else:
            self._init_message(received_data)

        bot_user_name = params.get('bot_user_name')

        if(bot_user_name is not None):
            self._message_link =\
                f'https://t.me/{bot_user_name}/{self._chat_id}?message_id={self._message_id}'
            

    def _init_message_from_dict(self, received_data):
        self._bot     = received_data['bot']
        self._chat_id = received_data['chat_id']
        self._message_id = received_data.get('message_id')
        self._user = received_data.get('user')

    def _init_message(self, message, callback_query = None, callback_data = None):

        self._bot            = message.bot
        self._message        = message
        self._callback_query = callback_query
        self._chat_id        = message.chat.id 
        self._message_id     = message.message_id
        self._callback_data = callback_data
        self._link          = None
        self._content_type  = message.content_type

        if( callback_query is None):
            self._from_user      = message.from_user
        else:
            self._from_user      = callback_query.from_user

        content_to_attr_map = {
            tgMessageTypes.VOICE: 'voice',
            tgMessageTypes.AUDIO: 'audio',
            tgMessageTypes.DOCUMENT: 'document',
            tgMessageTypes.PHOTO: 'photo',
        }

        content_attr = content_to_attr_map.get(self._message_type)

        if(content_attr is not None):
            content = getattr(message, content_attr )
            if(isinstance(content, list)):
                content = content[ len(content) - 1 ]
            self._file = content.to_python()

    @property
    def session_log(self):
        return self._session_log

    @session_log.setter
    def session_log(self, value):
        self._session_log = value

    @property
    def message_link(self):
        return self._message_link
    
    @property
    def content_type(self):
        return self._content_type
    
    @property 
    def callback_data(self):
        return self._callback_data
    
    @property
    def chat_id(self):
        return self._chat_id
    
    @property
    def user_id(self):
        return self._from_user.id

    @property
    def bot(self):
        return self._bot
    
    @property
    def message_id(self):
        return self._message_id
    
    @property
    def message_type(self):
        return self._message_type
    
    @property
    def user(self):
        return self._user
    
    @user.setter
    def user(self, user):
        self._user = user
    
    @abstractmethod 
    def send(self, string: str, menu = None):
        pass

    def get_content(self):

        if self.is_text():
            return self.get_text()
        elif self.is_command():
            return self.get_command_name()
        else:
            return ''
        
    def is_text(self):
        return self._message_type == tgMessageTypes.TEXT

    def is_inline(self):
        return ( self._message_type == tgMessageTypes.INLINE 
                or self._message_type == tgMessageTypes.CUSTOM_INLINE
        )

    def is_command(self):
        return self._message_type == tgMessageTypes.COMMAND
    
    def is_audio(self):
        return self._message_type == tgMessageTypes.AUDIO \
                or self._message_type == tgMessageTypes.VOICE

    def is_document(self):
        return self._message_type == tgMessageTypes.DOCUMENT
    
    def is_photo(self):
        return self._message_type == tgMessageTypes.PHOTO
    
    def is_file(self):

        return self.is_audio() or self.is_document() or self.is_photo()
    
    def get_menu_id(self):
        return self._callback_data.get('menu_id')

    def get_action_id(self):

        if(self._message_type == tgMessageTypes.INLINE):
            return self._callback_data.get('action_id')
        else:
            return self._message.text

    def get_action_data(self, type_func = None):
        value = self._callback_data.get('action_data')

        if(type_func is not None and value is not None):
            value = type_func(value)

        return value

    def get_command_name(self):
        return self._message.get_command()

    def get_text(self):
        return tgUtils.remove_markdown_symbols( self._message.text )
    
    def get_executer(self):
        return self._executer
    
    def get_task_queue(self, ):
        return self._task_queue
    
    async def download_file(self, target_format = None):

        config = Config()

        saving_folder = os.path.join( config.tg_bot.path_files, str(self._chat_id) )

        if not os.path.exists(saving_folder):
            os.makedirs(saving_folder)
        
        file = await self._bot.get_file(self._file['file_id'])

        file_location = os.path.join(saving_folder, file.file_path)

        source_file = await self._bot.download_file(
            file.file_path, 
            destination = file_location
        )
       
        if(self._message_type == tgMessageTypes.DOCUMENT):
            file_name = self._file['file_name']
        else:
            file_name = os.path.basename(file_location)

        return file_name, file_location, self.message_link
    
   

   



