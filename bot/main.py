import logging
import telebot

from db_manager import SqlManager
from logger import logger
from secured import TELEGRAM_TOKEN



# Создаем экземпляр бота
bot = telebot.TeleBot(token=TELEGRAM_TOKEN)

# Команда /start
@bot.message_handler(commands=["start"])
def handle_start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.first_name + (" " + message.from_user.last_name if message.from_user.last_name else "")

    logger.info(f"Пользователь {full_name} (ID: {user_id}) вызвал команду /start")

    # Добавляем пользователя в базу данных, если его еще нет
    try:
        # Создаем экземпляр SqlManager для работы с базой данных
        db = SqlManager(db_path="sqlite.db")
        db.add_user(username=username, telegram_id=user_id, full_name=full_name)
        bot.reply_to(message, f"Привет, {full_name}! Вы успешно зарегистрированы.")
        logger.info(f"Пользователь {full_name} успешно зарегистрирован.")
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при регистрации.")
        logger.error(f"Ошибка при регистрации пользователя {full_name}: {e}")


# Команда /add_task
@bot.message_handler(commands=["add_task"])
def handle_add_task(message):
    user_id = message.from_user.id
    full_name = message.from_user.first_name + (" " + message.from_user.last_name if message.from_user.last_name else "")

    logger.info(f"Пользователь {full_name} (ID: {user_id}) вызвал команду /add_task")

    # Запрашиваем у пользователя заголовок задачи
    bot.reply_to(message, "Введите заголовок задачи:")
    bot.register_next_step_handler(message, process_task_title, full_name)


def process_task_title(message, author):
    title = message.text
    logger.info(f"Пользователь {author} ввел заголовок задачи: {title}")

    # Запрашиваем у пользователя дедлайн задачи
    bot.reply_to(message, "Введите дедлайн задачи (в формате YYYY-MM-DD):")
    bot.register_next_step_handler(message, process_task_deadline, author, title)


def process_task_deadline(message, author, title):
    deadline = message.text
    logger.info(f"Пользователь {author} ввел дедлайн задачи: {deadline}")

    # Добавляем задачу в базу данных
    try:
        # Создаем экземпляр SqlManager для работы с базой данных
        db = SqlManager(db_path="sqlite.db")
        db.add_task(title=title, description=None, deadline=deadline, author=author)
        bot.reply_to(message, f"Задача '{title}' успешно добавлена!")
        logger.info(f"Задача '{title}' успешно добавлена пользователем {author}.")
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при добавлении задачи.")
        logger.error(f"Ошибка при добавлении задачи '{title}' пользователем {author}: {e}")


# Команда /list_tasks
@bot.message_handler(commands=["list_tasks"])
def handle_list_tasks(message):
    user_id = message.from_user.id
    full_name = message.from_user.first_name + (" " + message.from_user.last_name if message.from_user.last_name else "")

    logger.info(f"Пользователь {full_name} (ID: {user_id}) вызвал команду /list_tasks")
    # Создаем экземпляр SqlManager для работы с базой данных
    db = SqlManager(db_path="sqlite.db")
    tasks = db.get_tasks_list()

    if not tasks:
        bot.reply_to(message, "У вас пока нет задач.")
        logger.info(f"У пользователя {full_name} нет задач.")
        return

    response = "Ваши задачи:\n"
    for task in tasks:
        response += f"- {task['title']} (дедлайн: {task['deadline']})\n"

    bot.reply_to(message, response)
    logger.info(f"Список задач отправлен пользователю {full_name}.")


# Запуск бота
if __name__ == "__main__":
    logger.info("Бот запущен...")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске бота: {e}")
