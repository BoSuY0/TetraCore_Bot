import asyncio
import logging
import traceback
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.token import TokenValidationError
from config import BOT_TOKEN
from core.module import ModuleManager
from handlers import setup_handlers
from handlers.callback_handlers import setup_callback_handlers
from core.group_settings import GroupSettings
from core.admin_checker import AdminChecker

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Налаштування бота
def setup_bot(token: str) -> Bot:
    return Bot(token=token)

# Головна функція
async def main() -> None:
    logger.info("Бот запускається...")

    storage = MemoryStorage()
    bot = setup_bot(BOT_TOKEN)
    dp = Dispatcher(storage=storage)
    
    group_settings = GroupSettings()  # Підключення до бази даних
    admin_checker = AdminChecker(bot)
    module_manager = ModuleManager(bot=bot, group_settings=group_settings)
    
    # Налаштування обробників
    router = Router()
    setup_handlers(router, bot, module_manager, admin_checker, group_settings)
    setup_callback_handlers(router, module_manager)

    dp.include_router(router)

    try:
        logger.info("Починається опитування...")
        await dp.start_polling(bot, allowed_updates=['message', 'callback_query'])
    except TokenValidationError:
        logger.critical("Надано недійсний токен")
    except Exception as e:
        logger.error(f"Виникла критична помилка: {e}", exc_info=True)
    finally:
        await bot.session.close()
        logger.info("Бот зупинено")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот зупинено вручну")
    except Exception as e:
        logger.error(f"Виникла неочікувана помилка: {e}", exc_info=True)
