"""
This news trapper telegram bot
"""
import os
import sys
import json
import logging
import asyncio
import re
import pytz
from datetime import datetime
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, Dispatcher, executor, types
from db_controller import DBController
import config
sys.path.insert(0, 'scrapers')
from scraper_abstract import Scraper
# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config.API_TOKEN)
loop = asyncio.get_event_loop()
dp = Dispatcher(bot, storage=MemoryStorage(), loop=loop)

# DB inition
dbc = DBController()


def aggregate_news(db_controller):
    """Метод активирует скрэперы а далее вносит изменения в БД"""
    # Получаем список файлов скрэперво
    scrapers_folder_list = os.listdir('Scrapers')
    scrapers = []
    # Убираем лишние файлы из списка
    for file in scrapers_folder_list:
        avoidance_sheet = ['__pycache__', 'scraper_abstract.py', 'Scrapper.py']
        if file not in avoidance_sheet:
            scrapers.append(file)
    # Запускаем работу скрэперов
    for scraper in scrapers:
        try:
            exec(open("Scrapers/" + scraper, encoding="utf8").read())
        except Exception:
            print("ERROR: with " + scraper + "something went wrong")
    # Открываем полученные новости
    with open('temp/collected_data.json', 'r', encoding='utf-8') as file:
        news = json.load(file)
    """
    Старый вариант через статус (new/old) для каждой новости
    for item in news:
        response = db_controller.add_news(item["name"], item["source"], item["url"], item["text"])
        #Если новости не было в БД даем её статус new
        if response == "new":
            db_controller.update_relevance(item["url"], "new")
        #Если новости была в БД даем её статус old
        if response == "old":
            db_controller.update_relevance(item["url"], "old")
    """
    current_date_time = datetime.now(pytz.timezone('Europe/Moscow'))

    for item in news:
        db_controller.add_news(
            item["name"], item["source"], item["url"], item["text"])

    os.remove('temp/collected_data.json')
    print("HOT NEWS. TIME:"+str(current_date_time))
    return current_date_time


def check_user(telegram_id):
    """Проверить наличие пользователя,
       если он ещё не совершал действий в боте
       и его не в бд ТО добавить"""
    if dbc.check_user(telegram_id) is False:
        dbc.add_user(telegram_id)


def get_sources_name(command):
    """Получить исотчники"""
    ikb = InlineKeyboardMarkup(row_width=2)
    sources = dbc.from_source()
    if sources == []:
        return "Sources not found"
    else:
        for item in sources:
            ib = InlineKeyboardButton(
                text=item[0], callback_data=command + "$" + item[0])
            ikb.add(ib)
        return ikb


def get_subscriptions_name(telegram_id):
    """Получить подписки"""
    ikb = InlineKeyboardMarkup(row_width=2)
    sources = dbc.get_subscriptions(telegram_id)
    if sources == []:
        return "Sub not found"
    else:
        for item in sources:
            ib = InlineKeyboardButton(
                text=item[0], callback_data="unsubcribe" + "$" + item[0])
            ikb.add(ib)
        return ikb


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """Отправка информационного сообщения при команде start"""
    await message.answer("Привет! Это NewsTrapperBot!\nЭтот бот сможет собрать для тебя самые свежие новости!\nCreated by github.com/SveBB")
    await message.answer("Список команд:\n"+config.COMMANDS)


@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    """Отправка информационного сообщения при команде help"""
    await message.answer("Обратитесь к @tohellim для техподдержки!")


@dp.message_handler(commands=['from_source'])
async def send_sources(message: types.Message):
    """Показать новости из источников"""
    check_user(message.from_user.id)
    ikb_now = get_sources_name('from_source')
    if ikb_now == "Sources not found":
        await message.answer(text="Пока что список источников пуст")
    else:
        await message.answer(text="Посмотреть источник", reply_markup=ikb_now)


@dp.message_handler(commands=['subcribe'])
async def subscribe_sources(message: types.Message):
    """Подписка на источники"""
    check_user(message.from_user.id)
    ikb_now = get_sources_name('subcribe')
    if ikb_now == "Sources not found":
        await message.answer(text="Пока что список источников пуст")
    else:
        await message.answer(text="Подписаться на источник", reply_markup=ikb_now)


@dp.message_handler(commands=['unsubcribe'])
async def unsubscribe_sources(message: types.Message):
    """Отписка от источников"""
    check_user(message.from_user.id)
    ikb_now = get_subscriptions_name(message.from_user.id)
    if ikb_now == "Sub not found":
        await message.answer(text="Пока что у вас нет подписок")
    else:
        await message.answer(text="Отписаться от", reply_markup=ikb_now)


@dp.callback_query_handler()
async def callback_sources(callback: types.CallbackQuery):
    """Функция обработка callback"""
    callback_data = callback.data
    command = callback_data.split("$")[0]

    if command == 'from_source':
        update_user_n = dbc.get_update_n(callback.from_user.id)
        titles_from_source = dbc.select_news_from_source(
            callback.data.split("$")[1], update_user_n)
        if titles_from_source == []:
            await callback.message.answer("Пока нет новостей из данного источника")
        else:
            for title in titles_from_source:
                await callback.message.answer(str(callback.data.split("$")[1]) + "\n" + title[1] + "\nИсточник: "+title[0])

    if command == 'subcribe':
        response = dbc.add_subscription(
            telegram_id=callback.from_user.id, source=callback.data.split("$")[1])
        if response == "Subscribe added":
            await callback.message.answer("Вы подписались на " + callback.data.split("$")[1])
        if response == "Already signed":
            await callback.message.answer("Вы уже подписаны на " + callback.data.split("$")[1])

    if command == 'unsubcribe':
        response = dbc.del_subscription(
            telegram_id=callback.from_user.id, source=callback.data.split("$")[1])
        if response == "Subscribe deleted":
            await callback.message.answer("Вы отписались от " + callback.data.split("$")[1])
        else:
            await callback.message.answer("Ошибка")


class Mydialog(StatesGroup):
    """Хранилище состояние для уловливания сообщения после команды update_n"""
    answer = State()


@dp.message_handler(commands=['update_n'])
async def cmd_dialog(message: types.Message):
    """Команда для обноваления числа n новостей за раз для пользователя"""
    check_user(message.from_user.id)
    await Mydialog.answer.set()
    await message.answer("Сколько новостей вы хотите видеть за раз?\nВведите число от 1-50")


@dp.message_handler(state=Mydialog.answer)
async def process_message(message: types.Message, state: FSMContext):
    """Обработка выбора n"""
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


async def scheduled(wait_for, bot_dpc):
    """scheduler для переодической загрузки новых новостей и рассылке пользовтелям"""
    while True:
        update_time = aggregate_news(bot_dpc)
        bot_dpc.update_all_diff(update_time)

        users = bot_dpc.get_users()
        for user in users:
            # Получили подписки пользователя
            user_subs = bot_dpc.get_subscriptions(user[0])
            # Получили update n пользователя
            #update_user_n = bot_dpc.get_update_n(user[0])
            titles_new = []

            for sub in user_subs:
                #titles_new += bot_dpc.select_news_from_source(sub[0], update_user_n, relevance="new")
                wait_minute = wait_for/60
                titles_new += bot_dpc.get_news_where_diff(wait_minute, sub[0])

            if titles_new == []:
                pass
            else:
                await bot.send_message(user[0], text="НОВАЯ ПОДБОРКА НОВОСТЕЙ")
                for title in titles_new:
                    # await bot.send_message(user[0], text=title[3] + "\n" + title[1] + "\nИсточник: "+title[0])
                    await bot.send_message(user[0], text=title[0] + "\n" + title[1] + "\nИсточник: "+title[2])

        await asyncio.sleep(wait_for)

if __name__ == '__main__':
    wait_sec = config.NEWS_UPDATE_MINUTE*60
    dp.loop.create_task(scheduled(wait_sec, dbc))
    executor.start_polling(dp, skip_updates=True)
