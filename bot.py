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
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# DB inition
dbc = DBController()

class Mydialog(StatesGroup):
    otvet = State()

def aggregate_news(db_controller):
    """Метод активирует скрэперы а далее вносит изменения в БД"""
    scrapers_folder_list = os.listdir('Scrapers')
    scrapers = []
    for file in scrapers_folder_list:
        if file != '__pycache__' and file != 'scraper_abstract.py':
            scrapers.append(file)

    for scraper in scrapers:
        #try:
        exec(open("Scrapers/" + scraper, encoding="utf8").read())
        #except Exception:
            #print("ERROR: with " + scraper + "something went wrong")

    with open('temp/collected_data.json', 'r', encoding='utf-8') as file:
        news = json.load(file)

    for item in news:
        db_controller.add_news(item["name"], item["source"], item["url"], item["text"])

    os.remove('temp/collected_data.json')

def check_user(telegram_id):
    if dbc.check_user(telegram_id) == False:
        dbc.add_user(telegram_id)

def get_sources_name():
    ikb = InlineKeyboardMarkup(row_width=2)
    sources = dbc.from_source()
    for item in sources:
        ib = InlineKeyboardButton(text=item[0], callback_data=item[0])
        ikb.add(ib)
    return ikb

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm NewsTrapperBot!\nPowered by aiogram.\nCreated by github.com/SveBB")



@dp.message_handler(commands=['from_source'])
async def send_sources(message: types.Message):
    ikb_now = get_sources_name()
    check_user(message.from_user.id)
    await message.answer(text = "Посмотреть источник", reply_markup =ikb_now)


@dp.callback_query_handler()
async def callback_sources(callback: types.CallbackQuery):
    update_user_n = dbc.get_update_n(callback.from_user.id)
    titles_from_source = dbc.select_news_from_source(callback.data, update_user_n)
    for title in titles_from_source:
        await callback.message.answer(str(callback.data) + "\n" + title[1] + "\nИсточник: "+title[0])


class Mydialog(StatesGroup):
    answer = State()

@dp.message_handler(commands=['update_n'])
async def cmd_dialog(message: types.Message):
    await Mydialog.answer.set()
    await message.answer("Сколько новостей вы хотите видеть за раз?\nВведите число от 1-50")

# А здесь получаем ответ, указывая состояние и передавая сообщение пользователя
@dp.message_handler(state=Mydialog.answer)
async def process_message(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']
        result = dbc.add_update_n(message.from_user.id, user_message)
        if result == "Update n changed":
            otvet = "Вы выбрали количество новостей равное " + user_message
        else:
            otvet = "Что-то пошло не так попробуйте ещё раз\n/update_n"
        await message.answer(otvet)
    # Finish conversation
    await state.finish()

if __name__ == '__main__':
    #aggregate_news(dbc)
    executor.start_polling(dp, skip_updates=True)
