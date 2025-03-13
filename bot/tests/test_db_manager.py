import os
import pytest
from bot.db_manager import SqlManager
import sys

# Путь к временной базе данных для тестов
TEST_DB_PATH = "bot/tests/test_database.db"


@pytest.fixture
def db():
    """Фикстура для создания и очистки тестовой базы данных."""
    # Создаем экземпляр SqlManager с временной базой данных
    db = SqlManager(db_path=TEST_DB_PATH)
    # Создаем таблицы перед каждым тестом
    db.create_users_table()
    db.create_tasks_table()
    
    yield db  # Передаем экземпляр в тесты
    
    # Закрываем соединение и удаляем временную базу данных после теста
    db.close()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


def test_add_user(db):
    """Тест добавления пользователя."""
    db.add_user(username="test_user", telegram_id=12345, full_name="Test User")
    users = db.get_users_list()
    assert len(users) == 1
    assert users[0]["username"] == "test_user"
    assert users[0]["telegram_id"] == 12345
    assert users[0]["full_name"] == "Test User"


def test_add_task(db):
    """Тест добавления задачи."""
    db.add_user(username="test_user", telegram_id=12345, full_name="Test User")
    db.add_task(
        title="Test Task",
        description="This is a test task",
        deadline="2023-12-31",
        author="Test User",
        executor="Executor User"
    )
    tasks = db.get_tasks_list()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Test Task"
    assert tasks[0]["deadline"] == "2023-12-31"


def test_get_tasks_list(db):
    """Тест получения списка задач."""
    db.add_user(username="test_user", telegram_id=12345, full_name="Test User")
    db.add_task(
        title="Task 1",
        description="Description 1",
        deadline="2023-12-31",
        author="Test User"
    )
    db.add_task(
        title="Task 2",
        description="Description 2",
        deadline="2024-01-31",
        author="Test User"
    )
    tasks = db.get_tasks_list()
    assert len(tasks) == 2
    assert tasks[0]["title"] == "Task 1"
    assert tasks[1]["title"] == "Task 2"


def test_get_task_details(db):
    """Тест получения информации о конкретной задаче."""
    db.add_user(username="test_user", telegram_id=12345, full_name="Test User")
    db.add_task(
        title="Test Task",
        description="This is a test task",
        deadline="2023-12-31",
        author="Test User"
    )
    tasks = db.get_tasks_list()
    task_id = tasks[0]["id"]
    task_details = db.get_tasks_list(task_id=task_id)
    assert task_details["title"] == "Test Task"
    assert task_details["description"] == "This is a test task"
    assert task_details["deadline"] == "2023-12-31"
    assert task_details["author"] == "Test User"


def test_get_users_list(db):
    """Тест получения списка пользователей."""
    db.add_user(username="user1", telegram_id=11111, full_name="User One")
    db.add_user(username="user2", telegram_id=22222, full_name="User Two")
    users = db.get_users_list()
    assert len(users) == 2
    assert users[0]["username"] == "user1"
    assert users[1]["username"] == "user2"