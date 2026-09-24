from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db_async import (
    a_list_types, a_list_responsibles, a_add_event,
    a_get_event, a_list_all_events, a_delete_event,
)
from keyboards import (
    main_menu, cancel_kb, types_kb, responsibles_kb, skip_kb,
)

router = Router()


class EventForm(StatesGroup):
    title = State()
    type_id = State()
    responsible_id = State()
    start_at = State()
    reg_url = State()
    description = State()


@router.message(F.text == "➕ Добавить мероприятие")
async def add_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите название мероприятия:", reply_markup=cancel_kb())
    await state.set_state(EventForm.title)


@router.message(EventForm.title, F.text)
async def ev_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    types = await a_list_types()
    if not types:
        await message.answer("Нет ни одного типа. Добавьте через /add_type Название")
        await state.clear()
        return
    await message.answer("Выберите тип:", reply_markup=types_kb(types))
    await state.set_state(EventForm.type_id)


@router.callback_query(EventForm.type_id, F.data.startswith("type:"))
async def ev_type(cb: CallbackQuery, state: FSMContext):
    type_id = int(cb.data.split(":")[1])
    await state.update_data(type_id=type_id)
    rs = await a_list_responsibles()
    if not rs:
        await cb.message.edit_text("Нет ответственных. Добавьте через /add_resp Имя")
        await state.clear()
        return
    await cb.message.edit_text("Выберите ответственного:", reply_markup=responsibles_kb(rs))
    await state.set_state(EventForm.responsible_id)


@router.callback_query(EventForm.responsible_id, F.data.startswith("resp:"))
async def ev_resp(cb: CallbackQuery, state: FSMContext):
    resp_id = int(cb.data.split(":")[1])
    await state.update_data(responsible_id=resp_id)
    await cb.message.edit_text(
        "Введите дату и время начала:\n<code>ДД.ММ.ГГГГ ЧЧ:ММ</code>\n"
        "Например: <code>25.12.2025 18:30</code>"
    )
    await state.set_state(EventForm.start_at)


@router.message(EventForm.start_at, F.text)
async def ev_dt(message: Message, state: FSMContext):
    try:
        dt = datetime.strptime(message.text.strip(), "%d.%m.%Y %H:%M")
    except ValueError:
        await message.answer("❌ Неверный формат. Пример: 25.12.2025 18:30")
        return
    await state.update_data(start_at=dt.isoformat())
    await message.answer(
        "Отправьте ссылку на регистрацию или нажмите «Пропустить»:",
        reply_markup=skip_kb(),
    )
    await state.set_state(EventForm.reg_url)


@router.callback_query(EventForm.reg_url, F.data == "skip")
async def ev_skip_url(cb: CallbackQuery, state: FSMContext):
    await state.update_data(reg_url=None)
    await cb.message.edit_text("Введите описание или нажмите «Пропустить»:", reply_markup=skip_kb())
    await state.set_state(EventForm.description)


@router.message(EventForm.reg_url, F.text)
async def ev_url(message: Message, state: FSMContext):
    url = message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        await message.answer("Ссылка должна начинаться с http:// или https://")
        return
    await state.update_data(reg_url=url)
    await message.answer("Введите описание или нажмите «Пропустить»:", reply_markup=skip_kb())
    await state.set_state(EventForm.description)


@router.callback_query(EventForm.description, F.data == "skip")
async def ev_skip_desc(cb: CallbackQuery, state: FSMContext):
    await state.update_data(description=None)
    await cb.message.edit_text("Сохраняю...")
    await _save(cb.message, state)


@router.message(EventForm.description, F.text)
async def ev_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await _save(message, state)


async def _save(message: Message, state: FSMContext):
    data = await state.get_data()
    event_id = await a_add_event(
        title=data["title"],
        description=data.get("description"),
        start_at=datetime.fromisoformat(data["start_at"]),
        reg_url=data.get("reg_url"),
        type_id=data["type_id"],
        responsible_id=data["responsible_id"],
    )
    ev = await a_get_event(event_id)
    text = (
        f"✅ Мероприятие сохранено!\n\n"
        f"<b>{ev['title']}</b>\n"
        f"Тип: {ev['type_name']}\n"
        f"Когда: {ev['start_at']}\n"
        f"Ответственный: {ev['resp_name']}\n"
        f"Регистрация: {ev['reg_url'] or '—'}\n"
        f"Описание: {ev['description'] or '—'}"
    )
    await message.answer(text, reply_markup=main_menu())
    await state.clear()


@router.message(F.text == "📋 Все мероприятия")
async def all_events(message: Message):
    events = await a_list_all_events()
    if not events:
        await message.answer("Мероприятий пока нет.", reply_markup=main_menu())
        return
    lines = []
    for ev in events:
        lines.append(
            f"• <code>#{ev['id']}</code> {ev['start_at']} — <b>{ev['title']}</b> "
            f"({ev['type_name']}, отв.: {ev['resp_name']})"
        )
    await message.answer("\n".join(lines), reply_markup=main_menu())


@router.message(Command("del_event"))
async def del_event(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Использование: /del_event <id>")
        return
    ok = await a_delete_event(int(parts[1]))
    await message.answer("🗑 Удалено." if ok else "Не найдено.", reply_markup=main_menu())