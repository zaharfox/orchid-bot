from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import random

from data.orchid_data import CARE_TIPS
from utils.keyboards import care_tips_keyboard

router = Router()


@router.message(F.text == "💡 Советы по уходу")
async def care_tips(message: Message):
    await message.answer(
        "💡 <b>Советы по уходу за орхидеями</b>\n\n"
        "Выберите тему:",
        reply_markup=care_tips_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("tip_"))
async def show_tip(callback: CallbackQuery):
    tip_type = callback.data.replace("tip_", "")
    tips = CARE_TIPS.get(tip_type, [])

    headers = {
        "watering": "💧 Советы по поливу",
        "light": "☀️ Советы по освещению",
        "fertilizing": "🌿 Советы по подкормке",
        "repotting": "🪴 Советы по пересадке"
    }

    if not tips:
        await callback.answer("Нет советов по этой теме", show_alert=True)
        return

    text = f"<b>{headers.get(tip_type, 'Советы')}</b>\n\n"
    text += "\n\n".join(tips)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ Назад к темам", callback_data="back_care")

    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_care")
async def back_to_care(callback: CallbackQuery):
    await callback.message.edit_text(
        "💡 <b>Советы по уходу за орхидеями</b>\n\n"
        "Выберите тему:",
        reply_markup=care_tips_keyboard(),
        parse_mode="HTML"
    )
