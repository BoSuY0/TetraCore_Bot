import os
import json
from aiogram import Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from core.module import ModuleManager
import logging

logger = logging.getLogger(__name__)

def setup_handlers(router: Router, bot: Bot, module_manager: ModuleManager, admin_checker, group_settings):
    
    @router.message(CommandStart())
    async def command_start_handler(message: Message, state: FSMContext) -> None:
        logger.info(f"Отримано команду /start від користувача {message.from_user.id} в чаті {message.chat.id}")
        
        data = await state.get_data()
        
        if "started" not in data:
            welcome_message = (
                "👋 Привіт-привіт!\n\n"
                "Я — *TetraCore*, ваш вірний помічник у світі Telegram. 🌐\n\n"
                "Моя місія — допомогти вам створити найкращий досвід у вашому чаті за допомогою потужних і корисних модулів. "
                "Зі мною ви зможете активувати ігри 🎮, керувати групою ⚙️, і багато іншого! "
                "Просто скористайтеся командою /menu, щоб побачити доступні опції.\n\n"
                "💡 *Порада*: Якщо ви маєте питання або потребуєте допомоги, не соромтеся звертатися до мене!"
            )
            await message.answer(welcome_message, parse_mode="Markdown")
            
            await state.update_data(started=True)
        else:
            await menu_command_handler(message)

    @router.message(Command("activate"))
    async def activate_module_handler(message: Message) -> None:
        if message.chat.type != 'private':
            command_parts = message.text.split(maxsplit=1)
            if len(command_parts) > 1:
                module_name = command_parts[1]
                if await module_manager.check_admin_rights(message):
                    await module_manager.activate_module(message, module_name)
            else:
                await message.answer("Використання: /activate [назва_модуля]")
        else:
            await message.answer("Ця команда доступна тільки в групових чатах.")

    @router.message(Command("menu"))
    async def menu_command_handler(message: Message) -> None:
        modules_path = "modules/"
        
        total_modules = 0
        pro_modules = 0
        pro_plus_modules = 0
        game_modules = 0
        group_modules = 0
        utility_modules = 0
        other_modules = 0
        
        # Проходимо по всіх модулях і рахуємо їх категорії
        for module_name in os.listdir(modules_path):
            module_dir = os.path.join(modules_path, module_name)
            if os.path.isdir(module_dir):
                module_info_path = os.path.join(module_dir, "module_info.json")
                if os.path.exists(module_info_path):
                    with open(module_info_path, "r") as f:
                        module_info = json.load(f)
                        total_modules += 1
                        category = module_info.get("category", "Інше")
                        access_level = module_info.get("access_level", "free")
                        
                        if access_level == "pro":
                            pro_modules += 1
                        elif access_level == "pro_plus":
                            pro_plus_modules += 1

                        if category == "Ігри":
                            game_modules += 1
                        elif category == "Групові функції":
                            group_modules += 1
                        elif category == "Корисні інструменти":
                            utility_modules += 1
                        else:
                            other_modules += 1
        
        # Формуємо повідомлення з інформацією про модулі
        menu_message = (
            "📊 *Модульний Центр*\n\n"
            "🔢 Загальна кількість модулів: {total_modules}\n"
            "💎 Кількість модулів для Pro: {pro_modules}\n"
            "🏅 Кількість модулів для Pro+: {pro_plus_modules}\n\n"
            "🎮 *Ігри*: {game_modules}\n"
            "⚙️ *Групові функції*: {group_modules}\n"
            "🔧 *Корисні інструменти*: {utility_modules}\n"
            "🗃 *Інші модулі*: {other_modules}\n\n"
            "📜 Виберіть категорію, щоб побачити доступні модулі."
        ).format(
            total_modules=total_modules,
            pro_modules=pro_modules,
            pro_plus_modules=pro_plus_modules,
            game_modules=game_modules,
            group_modules=group_modules,
            utility_modules=utility_modules,
            other_modules=other_modules
        )

        # Відправляємо повідомлення з інформацією
        await message.answer(menu_message, parse_mode="Markdown")

        # Створюємо звичайну клавіатуру
        keyboard_buttons = []
        
        # Додаємо кнопки до списку кнопок
        if game_modules > 0:
            keyboard_buttons.append([KeyboardButton(text="🎮 Ігри")])
        if group_modules > 0:
            keyboard_buttons.append([KeyboardButton(text="⚙️ Групові функції")])
        if utility_modules > 0:
            keyboard_buttons.append([KeyboardButton(text="🔧 Корисні інструменти")])
        if other_modules > 0:
            keyboard_buttons.append([KeyboardButton(text="🗃 Інші модулі")])
        
        # Створюємо клавіатуру з кнопками
        keyboard = ReplyKeyboardMarkup(keyboard=keyboard_buttons, resize_keyboard=True)

        # Відправляємо повідомлення з клавіатурою
        await message.answer("Виберіть категорію:", reply_markup=keyboard)

    router.message.register(command_start_handler)
    router.message.register(activate_module_handler)
    router.message.register(menu_command_handler)
