from datetime import date, timedelta

from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Календарь"), KeyboardButton(text="➕ Добавить мероприятие")],
            [KeyboardButton(text="🗂 Типы"), KeyboardButton(text="👤 Ответственные")],
            [KeyboardButton(text="📋 Все мероприятия"), KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
    )


def types_kb(types) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for t in types:
        kb.button(text=t["name"], callback_data=f"type:{t['id']}")
    kb.adjust(2)
    return kb.as_markup()


def responsibles_kb(responsibles) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for r in responsibles:
        kb.button(text=r["name"], callback_data=f"resp:{r['id']}")
    kb.adjust(2)
    return kb.as_markup()


def skip_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Пропустить", callback_data="skip")]]
    )


def calendar_kb(days_with_events: dict[str, int]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    today = date.today()
    for i in range(30):
        d = today + timedelta(days=i)
        key = d.isoformat()
        count = days_with_events.get(key, 0)
        label = d.strftime("%d.%m")
        if count:
            label = f"🔴 {label} ({count})"
        kb.button(text=label, callback_data=f"day:{key}")
    kb.adjust(3)
    return kb.as_markup()


def event_card_kb(event) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if event["reg_url"]:
        kb.button(text="📝 Записаться", url=event["reg_url"])
    kb.button(text="⬅️ К календарю", callback_data="back_to_calendar")
    kb.adjust(1)
    return kb.as_markup()


def day_events_kb(events) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for ev in events:
        time_part = ev["start_at"].split(" ")[1]
        kb.button(text=f"{time_part} — {ev['title']}", callback_data=f"event:{ev['id']}")
    kb.button(text="⬅️ К календарю", callback_data="back_to_calendar")
    kb.adjust(1)
    return kb.as_markup()