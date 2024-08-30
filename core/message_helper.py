from aiogram.types import Message
from aiogram.utils.markdown import text, bold, italic, code, pre

class MessageHelper:
    @staticmethod
    def format_welcome_message() -> str:
        return text(
            bold("Привіт!"), 
            "Я ваш бот, готовий допомогти вам.",
            "Використовуйте команду /menu, щоб побачити доступні модулі.",
            sep="\n"
        )

    @staticmethod
    def format_module_description(module_name: str, description: str) -> str:
        return text(
            bold(f"Модуль: {module_name}"),
            italic(description),
            sep="\n"
        )

    @staticmethod
    def create_error_message(exception: Exception) -> str:
        return text(
            bold("Помилка:"),
            code(str(exception)),
            sep="\n"
        )
