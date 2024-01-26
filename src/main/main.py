

import asyncio
import argparse
import logging


from aiogram  import Bot, Dispatcher, types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from app.config.config import Config
from app.resources.resource_definitions import ResourceDefinition
from app.telegram_bot.bot_handler_registrer import BotHandlersRegister
from app.store.factories.datamapper_factory import DatamapperFactory
from app.store.factories.storage_config_factory import DBConfigFactory
from app.processors.tasks.task_manager import TaskManager
from app.processors.tasks.events_manager import EventsManager
from app.services.logging import setup_logger
#from app.services.logger.alogger import setup_logger
from app.processors.tasks.task_bitrix import TaskNotifyEventImportDataFromBitrix

from concurrent.futures import ThreadPoolExecutor

CONFIG_FILE = './app/config/boot.ini'


def parse_command_line() -> dict:

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test_mode", action='store_true', help='Test mode.')
    args, unknown = parser.parse_known_args()
    
    return {'test_mode': args.test_mode}

config = Config(
    config_store_type='env', 
    commandline_args=parse_command_line()
)

#alogger = setup_logger(__name__)
#logger = setup_logger(__name__, config)
logging.basicConfig(level=logging.ERROR)

MAX_WORKER_THREADS = 5

class BotMiddleWare(BaseMiddleware):

    def __init__(self, me, task_queue):

        super().__init__()
        self._executor = ThreadPoolExecutor(max_workers=MAX_WORKER_THREADS)
        self._task_queue = task_queue
        self._bot_user_name = me.username 
        

    async def on_pre_process_message(self, message:types.Message, data: dict):
       
        data['executor'] = self._executor
        data['task_queue'] = self._task_queue
        data['bot_user_name'] = self._bot_user_name

    async def on_pre_process_callback_query(self, inline_query, data):
        data['executor']      = self._executor
        data['task_queue']    = self._task_queue
        data['bot_user_name'] = self._bot_user_name

class app():

    @staticmethod
    async def run():
        #logger.info('START_MAIN_LOOP')

        config = await app.init_config()
        bot    = Bot(token=config.tg_bot.token)
        dp     = Dispatcher(bot)
        task_queue    = asyncio.Queue() 
        event_manager = EventsManager(task_queue)
        task_manager  = TaskManager(bot, task_queue)
        me            = await bot.get_me()

        dp.middleware.setup(LoggingMiddleware())
        dp.middleware.setup(BotMiddleWare(me, task_queue))

        handlers_register = BotHandlersRegister()

        await handlers_register.register_commands(bot)
        await handlers_register.register_handlers(dp)
        
        asyncio.create_task(task_manager.start())

        #tmp
        task = TaskNotifyEventImportDataFromBitrix(params={})
        await task.process(None)

        await dp.start_polling()

    @staticmethod
    async def init_config() -> Config:

        config    = Config(config_store_type='env', commandline_args=parse_command_line())
        DBConfigFactory(url=config.db.db_conn_str)
        ResourceDefinition(config.tg_bot.language)

        datamapper = DatamapperFactory(id='local').get()
        await datamapper.install()
       
        return config
   
if __name__ == '__main__':

    asyncio.run(app.run())

    

   