from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database.db import get_orchids_needing_care
from utils.keyboards import main_menu_keyboard

router = Router()


@router.message(F.text == "🔔 Проверить уход")
async def check_care(message: Message):
    needing_care = await get_orchids_needing_care(message.from_user.id)
    if not needing_care:
        await message.answer(
            "✅ <b>Всё в порядке!</b>\n\n"
            "Ваши орхидеи не нуждаются в уходе прямо сейчас 🌸",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
        return

    lines = ["⚠️ <b>Эти орхидеи нуждаются в уходе:</b>\n"]
    for orchid, needs in needing_care:
        lines.append(f"🌺 <b>{orchid[2]}</b> ({orchid[3]}):")
        for need in needs:
            lines.append(f"  • {need}")
        lines.append("")

    await message.answer(
        "\n".join(lines),
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )
