
import asyncio
from aiogram.types import BotCommand
from aiogram  import Bot, Dispatcher
from app.telegram_bot.bot_service import CallbackDataBuilder
from app.telegram_bot.bot_handlers import BotHandler
from aiogram.types import ContentType
from app.resources.enums import tgMessageTypes


from app.resources.resource_definitions import ResourceDefinition

class BotHandlersRegister():

    async def register_commands(self, bot: Bot):
        
        app_resources = ResourceDefinition()

        commands = [
            BotCommand(
                command = app_resources.command_start, 
                description = app_resources.command_start_descr
            ),
            #BotCommand(command=df.COMMAND_HELP  , description="Помощь"),
            #BotCommand(command=df.COMMAND_CANCEL, description="Сбросить")
        
        ]

        await bot.set_my_commands(commands)

    async def register_handlers(self, dp : Dispatcher):
        
        app_resources = ResourceDefinition()

        call_back_data = CallbackDataBuilder()

        #dp.register_chat_join_request_handler(cmd_join)
        dp.register_message_handler( 
            BotHandler(tgMessageTypes.COMMAND), 
            commands=self.remove_unsupported_symbols( app_resources.command_start) 
        )

        dp.register_message_handler( 
            BotHandler(tgMessageTypes.COMMAND), 
            commands=self.remove_unsupported_symbols(app_resources.command_admin) 
        )
        
        dp.register_callback_query_handler( 
            BotHandler(tgMessageTypes.INLINE), 
            call_back_data.handler_filter()
        )
        
        dp.register_message_handler(
            BotHandler(tgMessageTypes.VOICE), 
            content_types=[ContentType.VOICE]
        )
        
        dp.register_message_handler(
            BotHandler(tgMessageTypes.AUDIO), 
            content_types=[ContentType.AUDIO]
        )

        dp.register_message_handler(
            BotHandler(tgMessageTypes.DOCUMENT), 
            content_types=[ContentType.DOCUMENT]
        )

        dp.register_message_handler(
            BotHandler(tgMessageTypes.PHOTO), 
            content_types=[ContentType.PHOTO]
        )

        dp.register_message_handler(BotHandler(tgMessageTypes.TEXT))
        


    @staticmethod
    def remove_unsupported_symbols(command_str: str):
        return command_str.replace("/", "")