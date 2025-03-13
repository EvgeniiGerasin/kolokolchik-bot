from datetime import datetime, timedelta
import sqlite3

from main import logger


class SqlManager:

    def __init__(self, db_path='sqlite.db') -> None:
        self.conn: sqlite3.Connection = sqlite3.connect(database=db_path)
        self.cursor: sqlite3.Cursor = self.conn.cursor()
        self.db_path: str = db_path

    def close(self) -> None:
        """Закрывает соединение с базой данных."""
        logger.info('Close DB')
        self.conn.close()

    def check_table_exists(self, table_name: str) -> bool:
        """Проверяет существование таблицы в базе данных"""
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        result = self.cursor.fetchone()
        if result is None:
            return False
        else:
            return True

    def create_users_table(self) -> None:
        """Создает таблицу Users, если она не существует."""
        sql_create_users_table = """
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                telegram_id INTEGER UNIQUE NOT NULL,
                full_name TEXT NOT NULL
            );
        """
        try:
            self.cursor.execute(sql_create_users_table)
            self.conn.commit()
            print("Таблица 'Users' успешно создана.")
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблицы 'Users': {e}")

    def create_tasks_table(self) -> None:
        """Создает таблицу Tasks, если она не существует."""
        sql_create_tasks_table = """
            CREATE TABLE IF NOT EXISTS Tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                deadline TEXT NOT NULL,
                author TEXT NOT NULL,
                executor TEXT,
                created_date TEXT NOT NULL,
                completed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (author) REFERENCES Users(full_name)
            );
        """
        try:
            self.cursor.execute(sql_create_tasks_table)
            self.conn.commit()
            print("Таблица 'Tasks' успешно создана.")
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблицы 'Tasks': {e}")


def main():
    db = SqlManager()
    # Проверяем, существует ли таблица
    if not db.check_table_exists(table_name='Users'):
        db.create_users_table()
    else:
        print("Таблица 'chats' уже существует.")
    if not db.check_table_exists(table_name='Tasks'):
        db.create_tasks_table()
    else:
        print("Таблица 'issues' уже существует.")
    db.close()


if __name__ == '__main__':
    main()
