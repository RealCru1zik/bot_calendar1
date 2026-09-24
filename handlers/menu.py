from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards import main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Я бот-календарь.\n\n"
        "• ➕ Добавить мероприятие\n"
        "• 📅 Календарь — посмотреть по дням\n"
        "• 🗂 Типы — управление типами\n"
        "• 👤 Ответственные\n"
        "• 📋 Все мероприятия",
        reply_markup=main_menu(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Используй кнопки меню 👇", reply_markup=main_menu())


@router.message(F.text == "❌ Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отменено.", reply_markup=main_menu())