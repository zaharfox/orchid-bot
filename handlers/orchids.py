from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import date

from database.db import (
    get_user_orchids, get_orchid, add_orchid,
    update_orchid_care, delete_orchid, add_care_history, get_care_history
)
from utils.keyboards import (
    orchids_list_keyboard, orchid_actions_keyboard,
    add_species_keyboard, confirm_delete_keyboard, main_menu_keyboard
)
from data.orchid_data import ORCHID_SPECIES

router = Router()


class AddOrchidStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_species = State()
    waiting_for_color = State()


@router.message(F.text == "🌸 Мои орхидеи")
@router.message(Command("myorchids"))
async def my_orchids(message: Message):
    orchids = await get_user_orchids(message.from_user.id)
    if not orchids:
        await message.answer(
            "🌱 У вас пока нет орхидей в коллекции.\n\n"
            "Нажмите <b>➕ Добавить орхидею</b>, чтобы добавить первую!",
            reply_markup=main_menu_keyboard(),
            parse_mode="HTML"
        )
        return
    await message.answer(
        f"🌺 <b>Ваша коллекция</b> ({len(orchids)} шт.):\n\nВыберите орхидею:",
        reply_markup=orchids_list_keyboard(orchids),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "my_orchids")
async def my_orchids_cb(callback: CallbackQuery):
    orchids = await get_user_orchids(callback.from_user.id)
    if not orchids:
        await callback.message.edit_text(
            "🌱 У вас пока нет орхидей в коллекции.",
        )
        return
    await callback.message.edit_text(
        f"🌺 <b>Ваша коллекция</b> ({len(orchids)} шт.):\n\nВыберите орхидею:",
        reply_markup=orchids_list_keyboard(orchids),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("orchid_view_"))
async def view_orchid(callback: CallbackQuery):
    orchid_id = int(callback.data.split("_")[-1])
    orchid = await get_orchid(orchid_id, callback.from_user.id)
    if not orchid:
        await callback.answer("Орхидея не найдена", show_alert=True)
        return

    today = date.today()

    def days_info(last_date_str, interval):
        if not last_date_str:
            return "⚠️ Никогда"
        last = date.fromisoformat(last_date_str)
        days_ago = (today - last).days
        days_left = interval - days_ago
        if days_left <= 0:
            return f"⚠️ Нужно сейчас! ({days_ago} дн. назад)"
        return f"✅ {last_date_str} (через {days_left} дн.)"

    species_info = ORCHID_SPECIES.get(orchid[3], {})
    emoji = species_info.get("emoji", "🌺")

    text = f"""
{emoji} <b>{orchid[2]}</b>
📌 Вид: {orchid[3]}
🎨 Цвет цветков: {orchid[4] or 'не указан'}

<b>График ухода:</b>
💧 Полив: {days_info(orchid[5], orchid[8])}
🌿 Подкормка: {days_info(orchid[6], orchid[9])}
🪴 Пересадка: {days_info(orchid[7], orchid[10])}

📝 Заметки: {orchid[11] or 'нет'}
"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Проверить корни", callback_data=f"check_roots_{orchid_id}")
    builder.button(text="💧 Полил", callback_data=f"care_water_{orchid_id}")
    builder.button(text="🌿 Подкормил", callback_data=f"care_fertilize_{orchid_id}")
    builder.button(text="🪴 Пересадил", callback_data=f"care_repot_{orchid_id}")
    builder.button(text="📋 История ухода", callback_data=f"orchid_history_{orchid_id}")
    builder.button(text="🗑️ Удалить", callback_data=f"orchid_delete_{orchid_id}")
    builder.button(text="◀️ К списку", callback_data="my_orchids")
    builder.adjust(1, 2, 2, 1, 1)

    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data.startswith("check_roots_"))
async def check_roots(callback: CallbackQuery):
    orchid_id = int(callback.data.split("_")[-1])
    orchid = await get_orchid(orchid_id, callback.from_user.id)
    if not orchid:
        await callback.answer("Орхидея не найдена", show_alert=True)
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="🩶 Серебристые / белые", callback_data=f"roots_silver_{orchid_id}")
    builder.button(text="💚 Зелёные", callback_data=f"roots_green_{orchid_id}")
    builder.button(text="◀️ Назад", callback_data=f"orchid_view_{orchid_id}")
    builder.adjust(1)

    await callback.message.edit_text(
        f"🔍 <b>Проверка корней — {orchid[2]}</b>\n\n"
        "Посмотрите на корни через прозрачный горшок или достаньте растение.\n\n"
        "Какого цвета корни сейчас?",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("roots_silver_"))
async def roots_silver(callback: CallbackQuery):
    orchid_id = int(callback.data.split("_")[-1])
    orchid = await get_orchid(orchid_id, callback.from_user.id)

    builder = InlineKeyboardBuilder()
    builder.button(text="💧 Отметить полив", callback_data=f"care_water_{orchid_id}")
    builder.button(text="◀️ К орхидее", callback_data=f"orchid_view_{orchid_id}")
    builder.adjust(1)

    await callback.message.edit_text(
        f"🩶 <b>Корни серебристые / белые</b>\n\n"
        f"💧 <b>Орхидею «{orchid[2]}» нужно полить!</b>\n\n"
        "Серебристый цвет означает что субстрат сухой и растение испытывает жажду. "
        "Используйте погружной полив на 15–20 минут.",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("roots_green_"))
async def roots_green(callback: CallbackQuery):
    orchid_id = int(callback.data.split("_")[-1])
    orchid = await get_orchid(orchid_id, callback.from_user.id)

    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ К орхидее", callback_data=f"orchid_view_{orchid_id}")

    await callback.message.edit_text(
        f"💚 <b>Корни зелёные</b>\n\n"
        f"✅ <b>Орхидею «{orchid[2]}» поливать не нужно!</b>\n\n"
        "Зелёный цвет корней говорит о достаточном количестве влаги. "
        "Подождите пока корни не посветлеют до серебристого.",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("orchid_history_"))
async def orchid_history(callback: CallbackQuery):
    orchid_id = int(callback.data.split("_")[-1])
    orchid = await get_orchid(orchid_id, callback.from_user.id)
    if not orchid:
        await callback.answer("Орхидея не найдена", show_alert=True)
        return

    history = await get_care_history(orchid_id)

    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ К орхидее", callback_data=f"orchid_view_{orchid_id}")

    if not history:
        await callback.message.edit_text(
            f"📋 <b>История ухода — {orchid[2]}</b>\n\n"
            "Записей пока нет. Отмечайте уход кнопками и история будет заполняться автоматически.",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        return

    care_names = {"water": "💧 Полив", "fertilize": "🌿 Подкормка", "repot": "🪴 Пересадка"}
    lines = [f"📋 <b>История ухода — {orchid[2]}</b>\n"]
    for record in history[:20]:  # последние 20 записей
        care_label = care_names.get(record[0], record[0])
        lines.append(f"{care_label} — {record[1]}")

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("care_"))
async def care_action(callback: CallbackQuery):
    parts = callback.data.split("_")
    care_type = parts[1]
    orchid_id = int(parts[2])

    orchid = await get_orchid(orchid_id, callback.from_user.id)
    if not orchid:
        await callback.answer("Орхидея не найдена", show_alert=True)
        return

    await update_orchid_care(orchid_id, care_type)

    care_names = {"water": "полив", "fertilize": "подкормка", "repot": "пересадка"}
    care_emojis = {"water": "💧", "fertilize": "🌿", "repot": "🪴"}

    await callback.answer(
        f"{care_emojis[care_type]} {care_names[care_type].capitalize()} отмечена! ✅",
        show_alert=True
    )
    # Refresh view
    await view_orchid(callback)


@router.message(F.text == "➕ Добавить орхидею")
@router.message(Command("add"))
async def add_orchid_start(message: Message, state: FSMContext):
    await message.answer(
        "🌺 <b>Добавление новой орхидеи</b>\n\n"
        "Как вы хотите её назвать?\n"
        "<i>(Например: «Моя красавица», «Фиолетовая», «Подарок мамы»)</i>",
        parse_mode="HTML"
    )
    await state.set_state(AddOrchidStates.waiting_for_name)


@router.callback_query(F.data == "add_orchid")
async def add_orchid_cb(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "🌺 <b>Добавление новой орхидеи</b>\n\n"
        "Как вы хотите её назвать?\n"
        "<i>(Например: «Моя красавица», «Фиолетовая», «Подарок мамы»)</i>",
        parse_mode="HTML"
    )
    await state.set_state(AddOrchidStates.waiting_for_name)
    await callback.answer()


@router.message(AddOrchidStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer(
        f"✅ Отлично! Орхидея будет называться <b>«{message.text.strip()}»</b>\n\n"
        "Выберите вид орхидеи:",
        reply_markup=add_species_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(AddOrchidStates.waiting_for_species)


@router.callback_query(F.data.startswith("add_species_"), AddOrchidStates.waiting_for_species)
async def process_species(callback: CallbackQuery, state: FSMContext):
    species = callback.data.replace("add_species_", "")
    await state.update_data(species=species)
    await callback.message.edit_text(
        f"✅ Вид: <b>{species}</b>\n\n"
        "Опишите цвет цветков (необязательно):\n"
        "<i>(Введите цвет или напишите «пропустить»)</i>",
        parse_mode="HTML"
    )
    await state.set_state(AddOrchidStates.waiting_for_color)


@router.callback_query(F.data == "cancel_add")
async def cancel_add(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Добавление отменено.")


@router.message(AddOrchidStates.waiting_for_color)
async def process_color(message: Message, state: FSMContext):
    color = message.text.strip()
    if color.lower() in ("пропустить", "skip", "-"):
        color = None

    data = await state.get_data()
    species = data["species"]
    name = data["name"]

    species_data = ORCHID_SPECIES.get(species, {})
    watering_interval = species_data.get("watering_interval", 7)
    fertilizing_interval = species_data.get("fertilizing_interval", 14)

    await add_orchid(
        message.from_user.id, name, species, color,
        watering_interval, fertilizing_interval
    )
    await state.clear()

    emoji = species_data.get("emoji", "🌺")
    await message.answer(
        f"{emoji} <b>Орхидея добавлена!</b>\n\n"
        f"📌 Название: {name}\n"
        f"🌿 Вид: {species}\n"
        f"🎨 Цвет: {color or 'не указан'}\n\n"
        f"💧 Полив каждые {watering_interval} дней\n"
        f"🌿 Подкормка каждые {fertilizing_interval} дней\n\n"
        "Не забывайте отмечать уход, чтобы я мог присылать точные напоминания! 🌸",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("orchid_delete_"))
async def delete_orchid_confirm(callback: CallbackQuery):
    orchid_id = int(callback.data.split("_")[-1])
    orchid = await get_orchid(orchid_id, callback.from_user.id)
    if not orchid:
        await callback.answer("Орхидея не найдена", show_alert=True)
        return
    await callback.message.edit_text(
        f"⚠️ Вы уверены, что хотите удалить орхидею <b>«{orchid[2]}»</b>?\n\n"
        "Это действие нельзя отменить.",
        reply_markup=confirm_delete_keyboard(orchid_id),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("confirm_delete_"))
async def delete_orchid_action(callback: CallbackQuery):
    orchid_id = int(callback.data.split("_")[-1])
    orchid = await get_orchid(orchid_id, callback.from_user.id)
    name = orchid[2] if orchid else "орхидея"
    await delete_orchid(orchid_id, callback.from_user.id)
    await callback.message.edit_text(
        f"🗑️ Орхидея <b>«{name}»</b> удалена из коллекции.",
        parse_mode="HTML"
    )
