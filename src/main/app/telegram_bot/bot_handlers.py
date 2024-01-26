
from collections import defaultdict
from asyncio import Queue, create_task

from aiogram.types import Message
from app.telegram_bot.bot_message import tgUserMassage

from app.models.factories.domain_objects_factory import DomainClassFactory
from app.models.factories.enum_domain_objects import domainObjectTypes
from app.store.factories.datamapper_factory import DatamapperFactory
from app.processors.state_processor_manager import StateProcessorManager
from app.models.custom_models.session.user_settings_manager import UserSettingsManager
from app.resources.enums import tgMessageTypes


class BotHandler():
    """
    The BotHandler class is used to handle different types of user inputs: text, command and inline.
    """

    def __init__(self, handler_type: tgUserMassage) -> None:
        """
        Initialize the BotHandler class with the type of input to be handled.
        handler_type - a string representing the type of input. Possible values are 'command', 'inline' and 'text'
        """
        super().__init__()
        
        if handler_type not in tgMessageTypes:
            raise ValueError(f'Unsupported handler type - "{handler_type}"')

        self._handler_type = handler_type
        self._user_queue   = defaultdict(Queue)
        self._workers      = {}

    async def __call__(self, *args, **kwargs):
        """
        Override the call method to call the appropriate handler based on the type of input.
        """
        handler_func = getattr(self, f'_handle_{self._handler_type.value}')
        await handler_func(*args, **kwargs)

    async def _process(self, session):

        state_processor_manager = StateProcessorManager(session)

        if(session.message.is_command()):
            processor = state_processor_manager.get_processor_of_command(
                session, session.message.get_command_name()
            )
        else:
            processor = state_processor_manager.get_processor(session, session.state_id)

        prev_processor_id = session.state_id
        next_processor_id = await processor.process()
        next_processor    = state_processor_manager.get_processor(
            session, 
            next_processor_id
        )
        
        next_processor_id = next_processor.id

        run_pre_process = True
        while(run_pre_process):

            if( not prev_processor_id == next_processor_id):
                settings_manager   = UserSettingsManager(session)
                resetting_settings = next_processor.get_resetting_settings()
                settings_manager.reset(resetting_settings)

            prev_processor_id = next_processor_id
            next_processor_id = await next_processor.pre_process()

            if( prev_processor_id == next_processor_id):
                run_pre_process = False
            else:
                next_processor = state_processor_manager.get_processor(
                    session, 
                    next_processor_id
                )

        session.state_id = next_processor_id

    async def process_message(self, user_message : tgUserMassage):
        
        user = DomainClassFactory.create(
            domainObjectTypes.User,
            user_message.user_info()
        ) 
        session = DomainClassFactory.create(domainObjectTypes.Session, {'user':user, 'message':user_message})
        session_log = DomainClassFactory.create(domainObjectTypes.SessionLog, {'message':user_message})
       
        session_log.start_log()
        user_message.session_log = session_log

        datamapper = DatamapperFactory().get()
        datamapper.add_dataobject(session_log)
        await datamapper.write_dataobjects_to_db()

        datamapper.add_dataobject(session)
       
        async with datamapper as dm:
            await dm.fill_instance_from_db(session)
            user_message.user = session.user
            await self._process(session)

    async def worker(self, chat_id):
        while True:
            message = await self._user_queue[chat_id].get()
            await self.process_message(message)
            self._user_queue[chat_id].task_done()
    
    async def _handle(self, user_message : tgUserMassage):
        #await self._user_queue[user_message.chat_id].join()
        chat_id = user_message.chat_id
        await self._user_queue[chat_id].put(user_message)
        if chat_id not in self._workers or self._workers[chat_id].done():
            self._workers[chat_id] = create_task(self.worker(chat_id))
        
    async def _handle_text(self, message : Message, **kwargs):

       user_message = tgUserMassage(
           tgMessageTypes.TEXT, 
           message, 
           params = self._get_default_args(**kwargs)
        )
       await self._handle(user_message) 
      
    async def _handle_command(self, message, **kwargs):

        command = kwargs.get('command')
        
        user_message = tgUserMassage(
            tgMessageTypes.COMMAND, 
            message, 
            params = self._get_default_args(**kwargs)
        )
        await self._handle(user_message) 

    async def _handle_inline(self, callback, **kwargs):

        user_message = tgUserMassage(
            tgMessageTypes.INLINE, 
            callback, 
            callback_data = kwargs.get('callback_data'),
            params = self._get_default_args(**kwargs)
        )
        await self._handle(user_message)

    async def _handle_voice(self, message : Message, **kwargs):

        
        user_message = tgUserMassage(
            tgMessageTypes.VOICE,
            message, 
            params = self._get_default_args(**kwargs)
        )
        await self._handle(user_message)

    async def _handle_audio(self, message : Message, **kwargs):

        user_message = tgUserMassage(
            tgMessageTypes.AUDIO, 
            message, 
            params = self._get_default_args(**kwargs)
        )
        await self._handle(user_message)

    async def _handle_photo(self, message : Message, **kwargs):

        user_message = tgUserMassage(
            tgMessageTypes.PHOTO, 
            message, 
            params = self._get_default_args(**kwargs)
        )
        await self._handle(user_message)

    async def _handle_doc(self, message : Message, **kwargs):

        user_message = tgUserMassage(
            tgMessageTypes.DOCUMENT, 
            message, 
            params = self._get_default_args(**kwargs)
        )
        await self._handle(user_message)

    def _get_default_args(self, **kwargs):

        return {
            'executer'  : kwargs.get('executor'),
            'task_queue': kwargs.get('task_queue'),
            'bot_user_name': kwargs.get('bot_user_name')
        }

