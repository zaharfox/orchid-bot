from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import re

from database.db import update_notify_time, get_user
from utils.keyboards import settings_keyboard, main_menu_keyboard

router = Router()


class SettingsStates(StatesGroup):
    waiting_for_time = State()


@router.message(F.text == "⚙️ Настройки")
async def settings(message: Message):
    user = await get_user(message.from_user.id)
    notify_time = user[3] if user else "09:00"
    await message.answer(
        f"⚙️ <b>Настройки</b>\n\n"
        f"⏰ Время уведомлений: <b>{notify_time}</b>\n\n"
        "Что хотите изменить?",
        reply_markup=settings_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "set_notify_time")
async def set_notify_time(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "⏰ <b>Время уведомлений</b>\n\n"
        "Введите время в формате <b>ЧЧ:ММ</b>\n"
        "<i>Например: 08:00 или 19:30</i>",
        parse_mode="HTML"
    )
    await state.set_state(SettingsStates.waiting_for_time)


@router.message(SettingsStates.waiting_for_time)
async def process_time(message: Message, state: FSMContext):
    time_str = message.text.strip()
    if not re.match(r"^\d{2}:\d{2}$", time_str):
        await message.answer(
            "❌ Неверный формат. Введите время в виде ЧЧ:ММ\n"
            "<i>Например: 08:00 или 19:30</i>",
            parse_mode="HTML"
        )
        return

    hours, minutes = map(int, time_str.split(":"))
    if not (0 <= hours <= 23 and 0 <= minutes <= 59):
        await message.answer("❌ Некорректное время. Попробуйте ещё раз.")
        return

    await update_notify_time(message.from_user.id, time_str)
    await state.clear()
    await message.answer(
        f"✅ Время уведомлений установлено: <b>{time_str}</b>\n\n"
        "Теперь я буду напоминать об уходе за орхидеями в это время 🌸",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )
