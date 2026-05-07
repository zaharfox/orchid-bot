from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import random

from data.orchid_data import FACTS
from utils.keyboards import species_keyboard

router = Router()


@router.message(F.text == "🎲 Интересный факт")
@router.message(Command("fact"))
async def random_fact(message: Message):
    fact = random.choice(FACTS)
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="🎲 Ещё факт", callback_data="random_fact")
    await message.answer(
        f"🔍 <b>Знаете ли вы?</b>\n\n{fact}",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "random_fact")
async def random_fact_cb(callback: CallbackQuery):
    fact = random.choice(FACTS)
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.button(text="🎲 Ещё факт", callback_data="random_fact")
    await callback.message.edit_text(
        f"🔍 <b>Знаете ли вы?</b>\n\n{fact}",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.message(F.text == "📚 Виды орхидей")
async def orchid_species(message: Message):
    await message.answer(
        "📚 <b>Популярные виды орхидей</b>\n\n"
        "Выберите вид, чтобы узнать о нём подробнее:",
        reply_markup=species_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("species_"))
async def show_species(callback: CallbackQuery):
    from data.orchid_data import ORCHID_SPECIES
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    species_key = callback.data.replace("species_", "")
    info = ORCHID_SPECIES.get(species_key)

    if not info:
        await callback.answer("Вид не найден", show_alert=True)
        return

    tips_text = "\n".join([f"• {tip}" for tip in info.get("tips", [])])

    text = f"""
{info['emoji']} <b>{info['name']}</b>

📖 {info['description']}

💧 <b>Полив:</b> {info['watering']}
☀️ <b>Освещение:</b> {info['light']}
🌡️ <b>Температура:</b> {info['temperature']}
💦 <b>Влажность:</b> {info['humidity']}
🌿 <b>Подкормка:</b> {info['fertilizing']}
🪴 <b>Пересадка:</b> {info['repotting']}

💡 <b>Советы:</b>
{tips_text}
"""
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ Назад к видам", callback_data="back_species")
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "back_species")
async def back_species(callback: CallbackQuery):
    await callback.message.edit_text(
        "📚 <b>Популярные виды орхидей</b>\n\n"
        "Выберите вид, чтобы узнать о нём подробнее:",
        reply_markup=species_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    await callback.message.edit_text("Главное меню. Используйте кнопки ниже 👇")
