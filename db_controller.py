"""Класс для управления БД"""
import sqlite3
from datetime import datetime
import pytz


class DBController:
    """Класс для взаимодействия с БД"""

    def __init__(self):
        """Инициация БД (Создает таблицы если их нет)"""
        try:
            self.db = sqlite3.connect('DataStore.db')
        except Exception:
            print("Соединение нарушено")

        self.sql = self.db.cursor()

        self.db.execute("PRAGMA foreign_keys = 1")

        self.sql.execute("""CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT UNIQUE,
        update_n INTEGER(50) DEFAULT 5
        )""")
        self.db.commit()

        self.sql.execute("""CREATE TABLE IF NOT EXISTS news(
        news_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT(20),
        source TEXT NOT NULL,
        url TEXT UNIQUE,
        title TEXT NOT NULL,
        date DateTime NOT NULL,
        relevance TEXT(3),
        difference DateTime
        )""")
        self.db.commit()

        self.sql.execute("""CREATE TABLE IF NOT EXISTS subscriptions(
        sub_id INTEGER PRIMARY KEY,
        telegram_id TEXT,
        source TEXT
        )""")
        self.db.commit()
        print("DB inition")

    def get_news_where_diff(self, time, name):
        """Получить новости за выбранный период"""
        self.sql.execute(
            f"SELECT name, title, url, difference FROM news WHERE difference < '{time}' AND name = '{name}'")
        data = self.sql.fetchall()
        return data

    def update_all_diff(self, arrival):
        """Обновляет поле разницы времени"""
        self.sql.execute(
            f"UPDATE news SET difference = ROUND((JULIANDAY('{arrival}') - JULIANDAY(date)) * 1440)")
        self.db.commit()
        return "diff updateted"

    def update_time_diff(self, url, arrival):
        """Обновляет поле разницы времени для конкретной записи"""
        self.sql.execute(
            f"SELECT url, date, ROUND((JULIANDAY('{arrival}') - JULIANDAY(date)) * 1440) AS difference FROM news WHERE url = '{url}'")
        minute_dif = self.sql.fetchall()
        minute_dif = minute_dif[0][2]
        self.sql.execute(
            f"UPDATE news SET difference = '{minute_dif}' WHERE url = '{url}'")
        self.db.commit()

    def update_relevance(self, url, relevance):
        """Изменение статуса актуальности новости"""
        try:
            self.sql.execute(
                f"UPDATE news SET relevance = '{relevance}' WHERE url = '{url}'")
            self.db.commit()
            if relevance == "new":
                print("status NEW for " + url)
            if relevance == "old":
                print("status OLD for " + url)
        except Exception:
            print("status error " + url)

    def get_users(self):
        """Получить список пользователей"""
        try:
            self.sql.execute("SELECT telegram_id FROM users")
            data = self.sql.fetchall()
            return list(data)
        except Exception:
            return "Error with users list"

    def get_subscriptions(self, telegram_id):
        """Получить подписики пользовтеля"""
        try:
            self.sql.execute(
                f"SELECT source FROM subscriptions WHERE telegram_id = '{telegram_id}'")
            data = self.sql.fetchall()
            return list(data)
        except Exception:
            data = ["нет подписок"]
            return list(data)

    def add_subscription(self, telegram_id, source):
        """Добавление подписки пользовтеля"""
        self.sql.execute(
            f"SELECT sub_id FROM subscriptions WHERE telegram_id = '{telegram_id}' AND source = '{source}'")
        data = self.sql.fetchall()
        if data == []:
            self.sql.execute(
                "INSERT INTO subscriptions (telegram_id, source) VALUES(?, ?)",
                (telegram_id, source))
            self.db.commit()
            return "Subscribe added"
        else:
            return "Already signed"

    def del_subscription(self, telegram_id, source):
        """Отписка"""
        try:
            self.sql.execute(
                f"DELETE FROM subscriptions WHERE telegram_id = '{telegram_id}' AND source = '{source}'")
            self.db.commit()
            return "Subscribe deleted"
        except Exception:
            return "Subscribe deleted error"

    def add_user(self, telegram_id):
        """Добавление нового пользователя"""
        try:
            self.sql.execute(
                f"INSERT INTO users (telegram_id) VALUES ({telegram_id});")
            self.db.commit()
            return "User added" + telegram_id
        except Exception:
            return "User already exists"

    def check_user(self, telegram_id):
        """Проверка есть ли пользователь в БД"""
        self.sql.execute(
            f"SELECT user_id FROM users WHERE telegram_id = '{telegram_id}'")
        data = self.sql.fetchall()
        if data != []:
            return True
        else:
            return False

    def get_update_n(self, telegram_id):
        """Получить значение UPDATE_N для пользовтеля"""
        self.sql.execute(
            f"SELECT update_n FROM users WHERE telegram_id = '{telegram_id}'")
        data = self.sql.fetchall()
        return data[0][0]

    def add_news(self, name, source, url, title):
        """Добавление заголовка в хранилище"""
        try:
            current_date_time = datetime.now(pytz.timezone('Europe/Moscow'))
            self.sql.execute(
                "INSERT INTO news (name, source, url, title, date) VALUES(?, ?, ?, ?, ?)",
                (name, source, url, title, current_date_time))
            self.db.commit()
            print("ADDED SUCCESSFULLY " + url)
            return "new"
        except Exception:
            #print("Problem with (maybe title already in DB) " + url)
            return "old"

    def add_update_n(self, telegram_id, update_n):
        """Изменение кол-во новостей пользователя"""
        try:
            if int(update_n) >= 1 and int(update_n) <= 50:
                self.sql.execute(
                    f"UPDATE users SET update_n = '{update_n}' WHERE telegram_id = '{telegram_id}'")
                self.db.commit()
                return "Update n changed"
            else:
                return "update_n size error"
        except Exception:
            return "Update n error"

    def from_source(self):
        """Получить значения уникальныз источников"""
        try:
            self.sql.execute("SELECT DISTINCT name, source FROM news")
            data = self.sql.fetchall()
            return list(data)
        except Exception:
            return "Error with source list"

    def select_news_from_source(self, name, update_n, relevance="default"):
        """Получить update_n последних записей из источника"""
        if relevance == "default":
            self.sql.execute(
                f"SELECT url, title, date, name FROM news WHERE name = '{name}' ORDER BY date LIMIT '{update_n}'")
            data = self.sql.fetchall()
            data.reverse()
            return data
        else:
            self.sql.execute(
                f"SELECT url, title, date, name FROM news WHERE name = '{name}' AND relevance = '{relevance}' ORDER BY date LIMIT '{update_n}'")
            data = self.sql.fetchall()
            data.reverse()
            return data

    def select_actual_news_from_source(self, name, update_n):
        """Получить update_n последних НОВЫХ записей из источника"""
        self.sql.execute(
            f"SELECT url, title, date FROM news WHERE name = '{name}' ORDER BY date LIMIT '{update_n}'")
        data = self.sql.fetchall()
        data.reverse()
        return data

    def connect_db(self):
        """Установка соединения с БД"""
        self.db = sqlite3.connect('DataStore.db')
        print("DB connection established")

    def close_db(self):
        """Прекращение соединения с БД"""
        self.db.close()
        print("DB connection terminated")
