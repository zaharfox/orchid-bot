from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def main_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🌸 Мои орхидеи"),
        KeyboardButton(text="➕ Добавить орхидею")
    )
    builder.row(
        KeyboardButton(text="📚 Виды орхидей"),
        KeyboardButton(text="💡 Советы по уходу")
    )
    builder.row(
        KeyboardButton(text="🎲 Интересный факт"),
        KeyboardButton(text="⚙️ Настройки")
    )
    return builder.as_markup(resize_keyboard=True)


def species_keyboard():
    from data.orchid_data import ORCHID_SPECIES
    builder = InlineKeyboardBuilder()
    for key, val in ORCHID_SPECIES.items():
        builder.button(
            text=f"{val['emoji']} {key}",
            callback_data=f"species_{key}"
        )
    builder.button(text="◀️ Назад", callback_data="back_main")
    builder.adjust(2)
    return builder.as_markup()


def care_tips_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="💧 Полив", callback_data="tip_watering")
    builder.button(text="☀️ Освещение", callback_data="tip_light")
    builder.button(text="🌿 Подкормка", callback_data="tip_fertilizing")
    builder.button(text="🪴 Пересадка", callback_data="tip_repotting")
    builder.button(text="◀️ Назад", callback_data="back_main")
    builder.adjust(2)
    return builder.as_markup()


def orchid_actions_keyboard(orchid_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="💧 Полил", callback_data=f"care_water_{orchid_id}")
    builder.button(text="🌿 Подкормил", callback_data=f"care_fertilize_{orchid_id}")
    builder.button(text="🪴 Пересадил", callback_data=f"care_repot_{orchid_id}")
    builder.button(text="📋 Подробнее", callback_data=f"orchid_detail_{orchid_id}")
    builder.button(text="🗑️ Удалить", callback_data=f"orchid_delete_{orchid_id}")
    builder.button(text="◀️ К списку", callback_data="my_orchids")
    builder.adjust(2)
    return builder.as_markup()


def orchids_list_keyboard(orchids: list):
    builder = InlineKeyboardBuilder()
    for o in orchids:
        builder.button(
            text=f"🌺 {o[2]} ({o[3]})",
            callback_data=f"orchid_view_{o[0]}"
        )
    builder.button(text="➕ Добавить", callback_data="add_orchid")
    builder.adjust(1)
    return builder.as_markup()


def add_species_keyboard():
    from data.orchid_data import ORCHID_SPECIES
    builder = InlineKeyboardBuilder()
    for key, val in ORCHID_SPECIES.items():
        builder.button(
            text=f"{val['emoji']} {key}",
            callback_data=f"add_species_{key}"
        )
    builder.button(text="❌ Отмена", callback_data="cancel_add")
    builder.adjust(2)
    return builder.as_markup()


def confirm_delete_keyboard(orchid_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да, удалить", callback_data=f"confirm_delete_{orchid_id}")
    builder.button(text="❌ Нет, оставить", callback_data=f"orchid_view_{orchid_id}")
    builder.adjust(2)
    return builder.as_markup()


def settings_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="⏰ Время уведомлений", callback_data="set_notify_time")
    builder.button(text="◀️ Назад", callback_data="back_main")
    builder.adjust(1)
    return builder.as_markup()
