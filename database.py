import sqlite3
from sqlite3 import Connection
from datetime import datetime

DB_FILE = 'database.db'


class DatabaseManager:
    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file

    def get_connection(self) -> Connection:
        """Получение соединения с базой данных"""
        return sqlite3.connect(self.db_file)

    def create_tables(self):
        """Создание таблиц в базе данных"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                first_name TEXT NOT NULL,
                age INT NOT NULL,
                target TEXT NOT NULL,
                level INT DEFAULT 1
            );'''
        )

        # Таблица напоминаний
        cursor.execute(
            '''CREATE TABLE IF NOT EXISTS reminders (
                job_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                is_reminder_on BOOLEAN NOT NULL,
                remind_time DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );'''
        )

        conn.commit()
        conn.close()

    def register_user(self, user_id: int, username: str, first_name: str, age: int, target: str):
        """Регистрация нового пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''INSERT INTO users (user_id, username, first_name, age, target)
               VALUES (?, ?, ?, ?, ?)''',
            (user_id, username, first_name, age, target)
        )

        conn.commit()
        conn.close()

    def is_user_registered(self, user_id: int) -> bool:
        """Проверка, зарегистрирован ли пользователь"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()

        conn.close()
        return result is not None

    def get_user_firstname(self, user_id: int) -> str:
        """Получить имя пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT first_name FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()

        conn.close()
        return result[0] if result else ""

    def get_user_level(self, user_id: int) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT level FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()

        conn.close()
        return result[0] if result else 1

    def update_user_level(self, user_id: int, level: int) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('UPDATE users SET level = ? WHERE user_id = ?', (level, user_id))

        conn.commit()
        conn.close()


    # Reminders
    def check_is_reminder_on(self, user_id: int) -> bool:
        """Проверка, включены ли напоминания"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''
            SELECT 1
            FROM reminders
            WHERE user_id = ? AND is_reminder_on = TRUE
            ''',
            (user_id,)
        )
        result = cursor.fetchone()

        conn.close()
        return result is not None


    def update_reminder_status(self, user_id: int, is_reminder_on: bool):
        # Обновить статус напоминания.
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''
            UPDATE reminders
            SET is_reminder_on = ?
            WHERE user_id = ?
            ''',
            (is_reminder_on, user_id)
        )

        conn.commit()
        conn.close()


    def add_reminder(self, job_id: str, user_id: int, remind_time: datetime, is_reminder_on: bool):
        """Сохранить напоминание"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''INSERT INTO reminders (job_id, user_id, remind_time, is_reminder_on)
               VALUES (?, ?, ?, ?)''',
            (job_id, user_id, remind_time, is_reminder_on)
        )

        conn.commit()
        conn.close()

    def delete_reminder(self, job_id: str):
        """Удалить напоминание"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM reminders WHERE job_id = ?', (job_id,))

        conn.commit()
        conn.close()

    def get_all_on_reminders(self):
        """Получить все напоминания"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT job_id, user_id, remind_time FROM reminders WHERE is_reminder_on = TRUE')
        reminders = cursor.fetchall()

        conn.close()
        return reminders

    def is_reminder_exist(self, user_id: int):
        """Получить напоминание, если оно существует"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''
            SELECT job_id, user_id, remind_time, is_reminder_on
            FROM reminders
            WHERE user_id = ?
            ''',
            (user_id,)
        )
        reminder = cursor.fetchone()
        conn.close()
        return reminder

    def get_reminder_time(self, user_id: int):
        """Получить напоминание, если оно существует"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''
            SELECT remind_time
            FROM reminders
            WHERE user_id = ?
            ''',
            (user_id,)
        )
        reminder = cursor.fetchone()
        conn.close()
        return reminder[0]

    def update_reminder_time(self, user_id: int, remind_time: str):
        """Обновить время напоминания"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            '''
            UPDATE reminders
            SET remind_time = ?
            WHERE user_id = ?
            ''',
            (remind_time, user_id)
        )

        conn.commit()
        conn.close()

db = DatabaseManager()
