from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from database.db import add_user
from utils.keyboards import main_menu_keyboard

router = Router()

WELCOME_TEXT = """
🌸 <b>Добро пожаловать в OrchidBot!</b>

Я помогу вам вырастить здоровые и цветущие орхидеи 🌺

<b>Что я умею:</b>
• 🌺 Следить за вашей коллекцией орхидей
• 💧 Напоминать о поливе, подкормке и пересадке
• 📚 Рассказывать о разных видах орхидей
• 💡 Давать советы по уходу
• 🎲 Делиться интересными фактами

Выберите действие в меню ниже 👇
"""


@router.message(CommandStart())
async def cmd_start(message: Message):
    await add_user(message.from_user.id, message.from_user.username)
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard(), parse_mode="HTML")


@router.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
🌸 <b>Помощь по OrchidBot</b>

<b>Команды:</b>
/start — Главное меню
/help — Эта справка
/myorchids — Мои орхидеи
/add — Добавить орхидею
/fact — Случайный факт

<b>Кнопки меню:</b>
🌸 <b>Мои орхидеи</b> — список ваших растений
➕ <b>Добавить орхидею</b> — завести новое растение
📚 <b>Виды орхидей</b> — энциклопедия видов
💡 <b>Советы по уходу</b> — полив, свет, подкормка
🎲 <b>Интересный факт</b> — узнайте что-то новое
⚙️ <b>Настройки</b> — настроить уведомления
"""
    await message.answer(help_text, parse_mode="HTML")
