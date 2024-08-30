from telethon import TelegramClient, errors
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
import asyncio
import logging
import html
from aiogram import Bot
from config import API_ID, API_HASH, BOT_TOKEN  # Імпорт змінних з конфігураційного файлу

logger = logging.getLogger(__name__)

client = None

async def initialize_client():
    global client
    if client is None or not client.is_connected():
        client = TelegramClient('bot_session', API_ID, API_HASH)
        await client.start(bot_token=BOT_TOKEN)
        logger.info("Telethon client started")

async def get_all_members(chat_id):
    try:
        await initialize_client()
        chat = await client.get_entity(chat_id)
        all_participants = []
        offset = 0
        limit = 200
        while True:
            try:
                participants = await client(GetParticipantsRequest(
                    chat, ChannelParticipantsSearch(''), offset, limit,
                    hash=0
                ))
                if not participants.users:
                    break
                all_participants.extend(participants.users)
                offset += len(participants.users)
            except errors.ChatAdminRequiredError:
                logger.error("Bot needs to be an admin to fetch all members")
                return []
    except errors.ChannelPrivateError:
        logger.error("The channel/supergroup is private")
        return []
    except Exception as e:
        logger.error(f"Error in get_all_members: {e}")
        return []
    
    return all_participants

async def zaz_all(message, module_manager, bot: Bot):
    if not module_manager.is_module_active(message.chat.id, "pinger"):
        await message.reply("Ця команда доступна тільки при активному модулі 'Пінгер учасників'. Використайте /menu для активації.")
        return

    try:
        logger.info(f"Початок виконання zaz_all для групи {message.chat.id}")
        
        command_parts = message.text.split(maxsplit=1)
        custom_text = command_parts[1] if len(command_parts) > 1 else ""

        participants = await get_all_members(message.chat.id)
        logger.info(f"Отримано {len(participants)} учасників для групи {message.chat.id}")
        
        if not participants:
            await bot.send_message(message.chat.id, "Не вдалося отримати список учасників.")
            return

        mentions = []
        for user in participants:
            if user.bot:
                continue  # Пропускаємо ботів
            if user.username:
                # Використовуємо схожий Unicode символ для маскування '@'
                masked_username = user.username.replace('@', '\u200B@\u200B')
                mention = f'<a href="tg://user?id={user.id}">{masked_username}</a>'
            else:
                user_name = html.escape(user.first_name or f"User{user.id}")
                mention = f'<a href="tg://user?id={user.id}">{user_name}</a>'
            mentions.append(mention)
            logger.debug(f"Додано згадування для користувача {user.id} в групі {message.chat.id}: {mention}")

        # Розбиваємо згадування на частини по 10
        max_mentions_per_message = 10
        mention_chunks = [mentions[i:i + max_mentions_per_message] for i in range(0, len(mentions), max_mentions_per_message)]

        # Відправляємо повідомлення частинами
        for i, chunk in enumerate(mention_chunks, 1):
            mentions_text = ", ".join(chunk)
            chunk_message = f"{custom_text}\n\n{mentions_text}\n\nЧастина {i}/{len(mention_chunks)}"
            
            try:
                sent_message = await bot.send_message(message.chat.id, chunk_message, parse_mode="HTML")
                logger.info(f"Відправлено частину {i}/{len(mention_chunks)} для групи {message.chat.id}")
                logger.debug(f"Зміст відправленого повідомлення: {sent_message.text[:100]}...")
            except Exception as e:
                logger.error(f"Не вдалося відправити частину {i} для групи {message.chat.id}: {e}")
                await bot.send_message(message.chat.id, f"Виникла помилка при відправці частини {i} повідомлення.")
            
            await asyncio.sleep(0.5)

        # Відправляємо підсумкове повідомлення
        summary_message = f"\n\nЗгадано {len(mentions)} учасників.\nЯкщо ви бачите це повідомлення, будь ласка, відгукніться! 👋"
        await bot.send_message(message.chat.id, summary_message)
        logger.info(f"Завершено виконання zaz_all для групи {message.chat.id}")

    except Exception as e:
        logger.error(f"Неочікувана помилка в zaz_all для групи {message.chat.id}: {e}", exc_info=True)
        await bot.send_message(message.chat.id, "Виникла неочікувана помилка при виконанні команди.")
