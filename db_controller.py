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
        sources TEXT,
        update_n INTEGER(50) DEFAULT 5
        )""")
        self.db.commit()

        self.sql.execute("""CREATE TABLE IF NOT EXISTS news(
        news_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT(20),
        source TEXT NOT NULL,
        url TEXT UNIQUE,
        title TEXT NOT NULL,
        date DateTime NOT NULL
        )""")
        self.db.commit()
        print("DB inition")

    def add_user(self, telegram_id):
        """Добавление нового пользователя"""
        try:
            self.sql.execute(f"INSERT INTO users (telegram_id) VALUES ({telegram_id});")
            self.db.commit()
            print("User added" + telegram_id)
        except Exception:
            print("User already exists")

    def check_user(self, telegram_id):
        self.sql.execute(f"SELECT user_id FROM users WHERE telegram_id = '{telegram_id}'")
        data = self.sql.fetchall()
        if data != []:
            return True
        else:
            return False

    def get_update_n(self, telegram_id):
        self.sql.execute(f"SELECT update_n FROM users WHERE telegram_id = '{telegram_id}'")
        data = self.sql.fetchall()
        return data[0][0]

    def add_source(self, telegram_id, sources):
        """Изменение подписок пользователя"""
        try:
            self.sql.execute(f"UPDATE users SET sources = '{sources}' WHERE telegram_id = '{telegram_id}'")
            self.db.commit()
            print("Subscriptions changed")
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)

    def add_news(self, name, source, url, title):
        """Добавление заголовка в хранилище"""
        try:
            current_date_time = datetime.now(pytz.timezone('Europe/Moscow'))
            self.sql.execute(
                "INSERT INTO news (name, source, url, title, date) VALUES(?, ?, ?, ?, ?)",
                (name, source, url, title, current_date_time))
            self.db.commit()
            print("ADDED SUCCESSFULLY " + url)
        except Exception as inst:
            print(type(inst))
            print(inst.args)
            print(inst)

    def add_update_n(self, telegram_id, update_n):
        """Изменение кол-во новостей пользователя"""
        try:
            if int(update_n) >= 1 and int(update_n) <= 50:
                self.sql.execute(f"UPDATE users SET update_n = '{update_n}' WHERE telegram_id = '{telegram_id}'")
                self.db.commit()
                return "Update n changed"
            else:
                return "update_n size error"
        except Exception:
            return "Update n error"

    def from_source(self):
        try:
            self.sql.execute("SELECT DISTINCT name, source FROM news")
            data = self.sql.fetchall()
            print("SOURCE LIST")
            return list(data)
        except Exception:
            print("EMPTY LIST")

    def select_news_from_source(self, name, update_n):
        self.sql.execute(f"SELECT url, title, date FROM news WHERE name = '{name}' ORDER BY date LIMIT '{update_n}'")
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
