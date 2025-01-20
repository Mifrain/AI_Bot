import sqlite3
from datetime import datetime
from sqlite3 import Connection

DB_FILE = "database.db"


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
            """CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                first_name TEXT NOT NULL,
                age INT NOT NULL,
                target TEXT NOT NULL,
                level INT DEFAULT 1,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TEXT NOT NULL,
                survey_sent BOOLEAN DEFAULT FALSE
            );"""
        )

        # Таблица напоминаний
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS reminders (
                job_id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                is_reminder_on BOOLEAN NOT NULL,
                remind_time DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );"""
        )

        # Таблица Рейтинга
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS user_ratings (
                user_id INTEGER PRIMARY KEY,
                rating INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            );"""
        )

        conn.commit()
        conn.close()

    def register_user(
        self, user_id: int, username: str, first_name: str, age: int, target: str
    ):
        """Регистрация нового пользователя"""
        if self.is_user_registered(user_id):
            raise ValueError(f"User {user_id} is already registered.")

        conn = self.get_connection()
        cursor = conn.cursor()

        created_at = datetime.now().isoformat()

        cursor.execute(
            """INSERT INTO users (user_id, username, first_name, age, target, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, username, first_name, age, target, created_at),
        )

        conn.commit()
        conn.close()

    def is_user_registered(self, user_id: int) -> bool:
        """Проверка, зарегистрирован ли пользователь"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

        conn.close()
        return result is not None

    def get_user_firstname(self, user_id: int) -> str:
        """Получить имя пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT first_name FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

        conn.close()
        return result[0] if result else ""

    def get_user_level(self, user_id: int) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT level FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

        conn.close()
        return result[0] if result else 1

    def update_user_level(self, user_id: int, level: int) -> None:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET level = ? WHERE user_id = ?", (level, user_id))

        conn.commit()
        conn.close()

    # Reminders
    def check_is_reminder_on(self, user_id: int) -> bool:
        """Проверка, включены ли напоминания"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 1
            FROM reminders
            WHERE user_id = ? AND is_reminder_on = TRUE
            """,
            (user_id,),
        )
        result = cursor.fetchone()

        conn.close()
        return result is not None

    def update_reminder_status(self, user_id: int, is_reminder_on: bool):
        # Обновить статус напоминания.
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE reminders
            SET is_reminder_on = ?
            WHERE user_id = ?
            """,
            (is_reminder_on, user_id),
        )

        conn.commit()
        conn.close()

    def add_reminder(
        self, job_id: str, user_id: int, remind_time: datetime, is_reminder_on: bool
    ):
        """Сохранить напоминание"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO reminders (job_id, user_id, remind_time, is_reminder_on)
               VALUES (?, ?, ?, ?)""",
            (job_id, user_id, remind_time, is_reminder_on),
        )

        conn.commit()
        conn.close()

    def delete_reminder(self, job_id: str):
        """Удалить напоминание"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM reminders WHERE job_id = ?", (job_id,))

        conn.commit()
        conn.close()

    def get_all_on_reminders(self):
        """Получить все напоминания"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT job_id, user_id, remind_time FROM reminders WHERE is_reminder_on = TRUE"
        )
        reminders = cursor.fetchall()

        conn.close()
        return reminders

    def is_reminder_exist(self, user_id: int):
        """Получить напоминание, если оно существует"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT job_id, user_id, remind_time, is_reminder_on
            FROM reminders
            WHERE user_id = ?
            """,
            (user_id,),
        )
        reminder = cursor.fetchone()
        conn.close()
        return reminder

    def get_reminder_time(self, user_id: int):
        """Получить напоминание, если оно существует"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT remind_time
            FROM reminders
            WHERE user_id = ?
            """,
            (user_id,),
        )
        reminder = cursor.fetchone()
        conn.close()
        return reminder[0]

    def update_reminder_time(self, user_id: int, remind_time: str):
        """Обновить время напоминания"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE reminders
            SET remind_time = ?
            WHERE user_id = ?
            """,
            (remind_time, user_id),
        )

        conn.commit()
        conn.close()

    def is_user_admin(self, user_id: int) -> bool:
        """Проверка, является ли пользователь администратором"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT is_admin FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

        conn.close()
        return result[0] if result else False

    def update_user_rating(self, user_id: int, points: int) -> None:
        """Обновить рейтинг пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO user_ratings (user_id, rating)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET rating = rating + ?;
            """,
            (user_id, points, points),
        )

        conn.commit()
        conn.close()

    def get_top_and_user_position(self, user_id: int, limit: int = 5) -> dict:
        """
        Получить топ пользователей и позицию конкретного пользователя.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Получить топ-5 пользователей с их именами
        cursor.execute(
            """
            SELECT u.user_id, 
                COALESCE(u.username, u.first_name) AS display_name, 
                ur.rating
            FROM user_ratings ur
            JOIN users u ON ur.user_id = u.user_id
            ORDER BY ur.rating DESC
            LIMIT ?;
            """,
            (limit,),
        )
        top_users = cursor.fetchall()

        # Получить рейтинг текущего пользователя
        cursor.execute(
            """
            SELECT ur.rating
            FROM user_ratings ur
            WHERE ur.user_id = ?;
            """,
            (user_id,),
        )
        user_rating = cursor.fetchone()

        if user_rating is None:
            conn.close()
            return {
                "top_users": top_users,
                "user_position": -1,
                "user_rating": 0,
            }

        # Получить позицию текущего пользователя
        cursor.execute(
            """
            SELECT COUNT(*) + 1 AS position
            FROM user_ratings
            WHERE rating > ?;
            """,
            (user_rating[0],),
        )
        user_position = cursor.fetchone()[0]

        conn.close()

        return {
            "top_users": [
                {"user_id": user[0], "display_name": user[1], "rating": user[2]}
                for user in top_users
            ],
            "user_position": user_position,
            "user_rating": user_rating[0],
        }

    def get_user_count(self) -> int:
        """
        Получить количество пользователей в базе данных.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users;")
        total_users = cursor.fetchone()[0]

        conn.close()
        return total_users

    def get_users_for_survey(self):
        """
        Возвращает пользователей, которым нужно отправить напоминание об анкете.
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT user_id, created_at
            FROM users
            WHERE survey_sent = FALSE
            AND DATE(created_at, '+2 days') <= DATE('now');
            """
        )
        users = cursor.fetchall()
        conn.close()
        return users

    def mark_survey_sent(self, user_id):
        """
        Отмечает, что пользователю было отправлено напоминание об анкете.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET survey_sent = TRUE
            WHERE user_id = ?;
            """,
            (user_id,),
        )
        conn.commit()
        conn.close()


db = DatabaseManager()
