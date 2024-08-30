# Імпортуємо всі хендлери команд і callback-запитів
from .command_handlers import setup_handlers
from .callback_handlers import setup_callback_handlers

def setup_all_handlers(router, bot, module_manager, admin_checker, group_settings):
    setup_handlers(router, bot, module_manager, admin_checker, group_settings)
    setup_callback_handlers(router, module_manager)
