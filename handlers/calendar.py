from datetime import date, timedelta

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from db_async import a_count_events_by_day, a_list_events_for_day, a_get_event
from keyboards import calendar_kb, day_events_kb, event_card_kb

router = Router()


async def _render_calendar(target):
    today = date.today()
    horizon = today + timedelta(days=30)
    counts = await a_count_events_by_day(today.isoformat(), horizon.isoformat())
    text = "📅 Выберите день (🔴 — есть мероприятия):"
    kb = calendar_kb(counts)
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


@router.message(F.text == "📅 Календарь")
async def show_calendar(message: Message):
    await _render_calendar(message)


@router.callback_query(F.data == "back_to_calendar")
async def back(cb: CallbackQuery):
    await _render_calendar(cb)


@router.callback_query(F.data.startswith("day:"))
async def show_day(cb: CallbackQuery):
    day_str = cb.data.split(":", 1)[1]
    try:
        d = date.fromisoformat(day_str)
    except ValueError:
        await cb.answer("Ошибка даты", show_alert=True)
        return

    events = await a_list_events_for_day(day_str)
    if not events:
        await cb.message.edit_text(
            f"На {d.strftime('%d.%m.%Y')} мероприятий нет.",
            reply_markup=day_events_kb([]),
        )
        return

    await cb.message.edit_text(
        f"📅 {d.strftime('%d.%m.%Y')} — мероприятия ({len(events)}):",
        reply_markup=day_events_kb(events),
    )


@router.callback_query(F.data.startswith("event:"))
async def show_event(cb: CallbackQuery):
    ev_id = int(cb.data.split(":")[1])
    ev = await a_get_event(ev_id)
    if not ev:
        await cb.answer("Мероприятие не найдено", show_alert=True)
        return
    text = (
        f"🎯 <b>{ev['title']}</b>\n\n"
        f"🗂 Тип: {ev['type_name']}\n"
        f"🕒 Время: {ev['start_at']}\n"
        f"👤 Ответственный: {ev['resp_name']}\n"
        f"📝 Регистрация: {ev['reg_url'] or '—'}\n"
        f"📄 Описание: {ev['description'] or '—'}"
    )
    await cb.message.edit_text(text, reply_markup=event_card_kb(ev), disable_web_page_preview=True)