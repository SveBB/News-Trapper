"""
This news trapper telegram bot
"""
#import standart libs
import os
import sys
import json
import logging
import re
#____________________
import config
sys.path.insert(0, 'scrapers')
from scraper_abstract import Scraper
from db_controller import DBController
from aiogram import Bot, Dispatcher, executor, types

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

# DB inition
dbc = DBController()

def aggregate_news(db_controller):
    """Метод активирует скрэперы а далее вносит изменения в БД"""
    scrapers_folder_list = os.listdir('Scrapers')
    scrapers = []
    for file in scrapers_folder_list:
        if file != '__pycache__' and file != 'scraper_abstract.py':
            scrapers.append(file)

    for scraper in scrapers:
        try:
            exec(open("Scrapers/" + scraper).read())
        except Exception:
            print("ERROR: with " + scraper + "something went wrong")

    with open('temp/collected_data.json', 'r', encoding='utf-8') as file:
        news = json.load(file)

    for item in news:
        db_controller.add_news(item["source"], item["url"], item["text"])

    os.remove('temp/collected_data.json')


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm NewsTrapperBot!\nPowered by aiogram.\nCreated by github.com/SveBB")


@dp.message_handler(regexp='(^cat[s]?$|puss)')
async def cats(message: types.Message):
    with open('data/cats.jpg', 'rb') as photo:
        '''
        # Old fashioned way:
        await bot.send_photo(
            message.chat.id,
            photo,
            caption='Cats are here 😺',
            reply_to_message_id=message.message_id,
        )
        '''

        await message.reply_photo(photo, caption='Cats are here 😺')


@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)

    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
