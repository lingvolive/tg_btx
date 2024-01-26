import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils import executor

#import whisper
#import torch
#import os

#device = "cuda" if torch.cuda.is_available() else "cpu"

# Load the model 
#whisper_model = whisper.load_model("tiny", device=device)

#result = whisper_model.transcribe('tmpdata/audio/AgADVAoAAtFDgVU.oga')

#API_TOKEN = '5452322559:AAHGvVn0PoAohPy4A7ZICMMmLYlRQ6Xd9Dw'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    args = message.get_args()

    if args:
        await message.reply(f"You have entered the deep link parameter: {args}")
    else:
        await message.reply("Welcome to the Deep Link bot! Use /generate_deep_link to create a deep link.")

@dp.message_handler(commands=['generate_deep_link'])
async def generate_deep_link(message: types.Message):
    me = await bot.get_me()
    bot_username = me.username
    deep_link_parameter = "example_parameter"
    deep_link_url = f"https://t.me/{bot_username}?start={deep_link_parameter}"

    await message.reply(f"Here is your deep link:\n\n [<-Back]({deep_link_url})", parse_mode=ParseMode.MARKDOWN)

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)