import os
import json
import logging
from typing import Dict, Optional
from aiogram import Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from enum import Enum

logger = logging.getLogger(__name__)

class UserAccessLevel(Enum):
    FREE = "free"
    TRIAL = "trial"
    PRO = "pro"
    PRO_PLUS = "pro_plus"

class ModuleManager:
    def __init__(self, bot: Bot, group_settings):
        self.bot = bot
        self.group_settings = group_settings
        self.modules = {}
        self.active_modules: Dict[int, str] = {}
        self.load_modules()

    def load_modules(self):
        modules_path = "modules/"
        for module_name in os.listdir(modules_path):
            module_dir = os.path.join(modules_path, module_name)
            if os.path.isdir(module_dir) and os.path.exists(os.path.join(module_dir, "module_info.json")):
                with open(os.path.join(module_dir, "module_info.json"), "r") as f:
                    module_info = json.load(f)
                    self.modules[module_name] = module_info
                    logger.info(f"Завантажено модуль: {module_name}")

    async def check_admin_rights(self, message: Message) -> bool:
        chat_id = message.chat.id
        try:
            chat_member = await self.bot.get_chat_member(chat_id, self.bot.id)
            is_admin = chat_member.is_chat_admin() or chat_member.is_chat_owner()
            if not is_admin:
                await message.answer("Будь ласка, надайте мені права адміністратора для повноцінної роботи.")
            return is_admin
        except Exception as e:
            logger.error(f"Помилка при перевірці прав адміністратора: {e}", exc_info=True)
            await message.answer("Виникла помилка при перевірці прав. Спробуйте ще раз пізніше.")
            return False

    async def activate_module(self, message: Message, module_name: str) -> None:
        if module_name in self.modules:
            chat_id = message.chat.id
            self.active_modules[chat_id] = module_name
            self.group_settings.save_active_module(chat_id, module_name)
            await message.answer(f"Модуль '{module_name}' активовано для цієї групи.")
        else:
            await message.answer("Невідомий модуль. Будь ласка, перевірте правильність назви.")

    async def menu_command(self, message: Message) -> None:
        if message.chat.type == 'private':
            await self.handle_private_menu(message)
        else:
            await self.handle_group_menu(message)

    async def handle_private_menu(self, message: Message) -> None:
        modules_list = "\n".join([
            f"{module_info['name']} - {module_info['description']}" for module_info in self.modules.values()
        ])
        await message.answer(f"Доступні модулі:\n{modules_list}")

    async def handle_group_menu(self, message: Message) -> None:
        if not await self.check_admin_rights(message):
            return
        
        active_module = self.active_modules.get(message.chat.id)
        if active_module:
            await message.answer(
                f"Поточний активний модуль: {active_module}. Оберіть новий модуль для перемикання:",
                reply_markup=self.create_module_keyboard().as_markup()
            )
        else:
            await message.answer(
                "Оберіть модуль для активації:",
                reply_markup=self.create_module_keyboard().as_markup()
            )

    def create_module_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup()
        for module_name in self.modules:
            keyboard.add(InlineKeyboardButton(text=self.modules[module_name]["name"], callback_data=f"module_{module_name}"))
        return keyboard

    async def handle_module_selection(self, call: CallbackQuery):
        module_name = call.data.split('_', 1)[1]
        chat_id = call.message.chat.id
        
        if call.message.chat.type != 'private':
            if await self.check_admin_rights(call.message):
                self.active_modules[chat_id] = module_name
                self.group_settings.save_active_module(chat_id, module_name)
                await call.message.edit_text(f"Модуль '{module_name}' активовано.")
                await call.answer(f"Модуль '{module_name}' успішно активовано!")
            else:
                await call.answer("Бот не має прав адміністратора.")
        else:
            await call.answer("Цей модуль не можна активувати в приватному чаті.")
