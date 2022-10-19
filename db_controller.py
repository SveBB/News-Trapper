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
        sources TEXT
        )""")
        self.db.commit()

        self.sql.execute("""CREATE TABLE IF NOT EXISTS news(
        news_id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            print("User added")
        except Exception:
            print("User already exists")

    def add_source(self, telegram_id, sources):
        """Изменение подписок пользователя"""
        try:
            self.sql.execute(f"UPDATE users SET sources = '{sources}' WHERE telegram_id = '{telegram_id}'")
            self.db.commit()
            print("Subscriptions changed")
        except Exception:
            print("Subscriptions error")

    def add_news(self, source, url, title):
        """Добавление заголовка в хранилище"""
        try:
            current_date_time = datetime.now(pytz.timezone('Europe/Moscow'))
            self.sql.execute(
                "INSERT INTO news (source, url, title, date) VALUES(?, ?, ?, ?)",
                (source, url, title, current_date_time))
            self.db.commit()
            print("ADDED SUCCESSFULLY " + url)
        except Exception:
            print("already exists " + url)

    def connect_db(self):
        """Установка соединения с БД"""
        self.db = sqlite3.connect('DataStore.db')
        print("DB connection established")

    def close_db(self):
        """Прекращение соединения с БД"""
        self.db.close()
        print("DB connection terminated")
