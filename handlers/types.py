from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from config import ADMIN_IDS
from db_async import a_list_types, a_add_type, a_delete_type, a_list_responsibles, a_add_responsible
from keyboards import main_menu

router = Router()


@router.message(F.text == "🗂 Типы")
async def list_types(message: Message):
    types = await a_list_types()
    text = "Типы мероприятий:\n" + ("\n".join(f"• {t['name']}" for t in types) if types else "— пусто")
    text += "\n\nДобавить: /add_type Название\nУдалить: /del_type Название"
    await message.answer(text, reply_markup=main_menu())


@router.message(Command("add_type"))
async def add_type(message: Message):
    if ADMIN_IDS and message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Только для админов.")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /add_type Конференция")
        return
    name = parts[1].strip()
    ok = await a_add_type(name)
    await message.answer(
        f"✅ Тип «{name}» добавлен." if ok else "Такой тип уже есть.",
        reply_markup=main_menu(),
    )


@router.message(Command("del_type"))
async def del_type(message: Message):
    if ADMIN_IDS and message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ Только для админов.")
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /del_type Конференция")
        return
    name = parts[1].strip()
    result = await a_delete_type(name)
    if result == "ok":
        await message.answer(f"🗑 Тип «{name}» удалён.", reply_markup=main_menu())
    elif result == "in_use":
        await message.answer("Нельзя удалить — есть мероприятия этого типа.", reply_markup=main_menu())
    else:
        await message.answer("Не найдено.", reply_markup=main_menu())


@router.message(F.text == "👤 Ответственные")
async def list_resp(message: Message):
    rs = await a_list_responsibles()
    text = "Ответственные:\n" + ("\n".join(f"• {r['name']}" for r in rs) if rs else "— пусто")
    text += "\n\nДобавить: /add_resp Иван Иванов"
    await message.answer(text, reply_markup=main_menu())


@router.message(Command("add_resp"))
async def add_resp(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: /add_resp Иван Иванов")
        return
    name = parts[1].strip()
    ok = await a_add_responsible(name)
    await message.answer(
        f"✅ Ответственный «{name}» добавлен." if ok else "Уже есть.",
        reply_markup=main_menu(),
    )