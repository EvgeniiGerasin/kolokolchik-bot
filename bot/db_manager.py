from datetime import datetime
import sqlite3

from .main import logger


class SqlManager:

    def __init__(self, db_path='sqlite.db') -> None:
        """Инициализирует соединение с базой данных.

        Args:
            db_path (str): Путь к файлу базы данных SQLite.
        """
        self.conn: sqlite3.Connection = sqlite3.connect(database=db_path)
        self.cursor: sqlite3.Cursor = self.conn.cursor()
        self.db_path: str = db_path
        logger.info(f"Соединение с базой данных '{db_path}' установлено.")

    def close(self) -> None:
        """Закрывает соединение с базой данных."""
        logger.info("Закрытие соединения с базой данных.")
        self.conn.close()

    def check_table_exists(self, table_name: str) -> bool:
        """Проверяет существование таблицы в базе данных.

        Args:
            table_name (str): Имя таблицы для проверки.

        Returns:
            bool: True, если таблица существует, иначе False.
        """
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        result = self.cursor.fetchone()
        if result is None:
            logger.info(f"Таблица '{table_name}' не существует.")
            return False
        else:
            logger.info(f"Таблица '{table_name}' уже существует.")
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
            logger.info("Таблица 'Users' успешно создана.")
        except sqlite3.Error as e:
            logger.error(f"Ошибка при создании таблицы 'Users': {e}")

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
                FOREIGN KEY (author) REFERENCES Users(full_name),
                FOREIGN KEY (executor) REFERENCES Users(full_name)
            );
        """
        try:
            self.cursor.execute(sql_create_tasks_table)
            self.conn.commit()
            logger.info("Таблица 'Tasks' успешно создана.")
        except sqlite3.Error as e:
            logger.error(f"Ошибка при создании таблицы 'Tasks': {e}")

    def add_user(
        self,
        username: str,
        telegram_id: int,
        full_name: str
    ) -> None:
        """Добавляет нового пользователя в таблицу Users.

        Args:
            username (str): Уникальное имя пользователя.
            telegram_id (int): Уникальный ID пользователя в Telegram.
            full_name (str): Полное имя пользователя.

        Raises:
            sqlite3.IntegrityError: Если username или telegram_id уже существуют.
        """
        sql_add_user = """
            INSERT INTO Users (username, telegram_id, full_name)
            VALUES (?, ?, ?);
        """
        try:
            self.cursor.execute(sql_add_user, (username, telegram_id, full_name))
            self.conn.commit()
            logger.info(f"Пользователь '{full_name}' успешно добавлен.")
        except sqlite3.IntegrityError as e:
            logger.error(f"Ошибка при добавлении пользователя '{full_name}': {e}")
        except sqlite3.Error as e:
            logger.error(f"Неизвестная ошибка при добавлении пользователя '{full_name}': {e}")

    def add_task(
        self,
        title: str,
        author: str,
        deadline: str,
        description: str = None,
        executor: str = None
    ) -> None:
        """Добавляет новую задачу в таблицу Tasks.

        Args:
            title (str): Заголовок задачи.
            description (str, optional): Описание задачи. Defaults to None.
            deadline (str): Дедлайн задачи (в формате строки, например, "YYYY-MM-DD").
            author (str): Автор задачи (полное имя пользователя).
            executor (str, optional): Исполнитель задачи. Defaults to None.

        Raises:
            sqlite3.Error: При возникновении ошибки при добавлении задачи.
        """
        created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Текущая дата и время
        sql_add_task = """
            INSERT INTO Tasks (title, description, deadline, author, executor, created_date)
            VALUES (?, ?, ?, ?, ?, ?);
        """
        try:
            self.cursor.execute(
                sql_add_task,
                (title, description, deadline, author, executor, created_date)
            )
            self.conn.commit()
            logger.info(f"Задача '{title}' успешно добавлена.")
        except sqlite3.Error as e:
            logger.error(f"Ошибка при добавлении задачи '{title}': {e}")

    def get_tasks_list(self, task_id: int = None):
        """Получает список задач или информацию о конкретной задаче.

        Args:
            task_id (int, optional): ID задачи для получения полной информации. Defaults to None.

        Returns:
            list or dict: Список задач или словарь с информацией о конкретной задаче.
        """
        if task_id is None:
            # Получаем краткий список задач
            sql_get_tasks = """
                SELECT id, title, deadline FROM Tasks;
            """
            try:
                self.cursor.execute(sql_get_tasks)
                tasks = self.cursor.fetchall()
                logger.info("Список задач успешно получен.")
                return [{"id": task[0], "title": task[1], "deadline": task[2]} for task in tasks]
            except sqlite3.Error as e:
                logger.error(f"Ошибка при получении списка задач: {e}")
                return []
        else:
            # Получаем полную информацию о конкретной задаче
            sql_get_task = """
                SELECT title, description, deadline, author, executor, created_date, completed
                FROM Tasks
                WHERE id = ?;
            """
            try:
                self.cursor.execute(sql_get_task, (task_id,))
                task = self.cursor.fetchone()
                if task:
                    logger.info(f"Информация о задаче с ID {task_id} успешно получена.")
                    return {
                        "title": task[0],
                        "description": task[1],
                        "deadline": task[2],
                        "author": task[3],
                        "executor": task[4],
                        "created_date": task[5],
                        "completed": task[6]
                    }
                else:
                    logger.warning(f"Задача с ID {task_id} не найдена.")
                    return None
            except sqlite3.Error as e:
                logger.error(f"Ошибка при получении информации о задаче с ID {task_id}: {e}")
                return None

    def get_users_list(self):
        """Получает список всех пользователей.

        Returns:
            list: Список пользователей.
        """
        sql_get_users = """
            SELECT username, telegram_id, full_name FROM Users;
        """
        try:
            self.cursor.execute(sql_get_users)
            users = self.cursor.fetchall()
            logger.info("Список пользователей успешно получен.")
            return [{"username": user[0], "telegram_id": user[1], "full_name": user[2]} for user in users]
        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении списка пользователей: {e}")
            return []


def main():
    db = SqlManager()
    
    # Проверяем, существует ли таблица Users
    if not db.check_table_exists(table_name='Users'):
        db.create_users_table()
    # Проверяем, существует ли таблица Tasks
    if not db.check_table_exists(table_name='Tasks'):
        db.create_tasks_table()
    db.close()


if __name__ == '__main__':
    main()