from aiogram import Router
from aiogram.types import CallbackQuery
from core.module import ModuleManager
import logging

logger = logging.getLogger(__name__)

def setup_callback_handlers(router: Router, module_manager: ModuleManager):
    
    @router.callback_query(lambda call: call.data.startswith("category_"))
    async def handle_category_selection(call: CallbackQuery):
        category = call.data.split('_', 1)[1]
        
        # Тут ви можете визначити логіку для кожної категорії
        if category == "games":
            await call.message.answer("Ви обрали категорію 🎮 Ігри.")
        elif category == "group":
            await call.message.answer("Ви обрали категорію ⚙️ Групові функції.")
        elif category == "utility":
            await call.message.answer("Ви обрали категорію 🔧 Корисні інструменти.")
        elif category == "other":
            await call.message.answer("Ви обрали категорію 🗃 Інші модулі.")
        
        # Обов'язково відповідайте на callback, щоб закрити його
        await call.answer()

    router.callback_query.register(handle_category_selection)
