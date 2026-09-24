from aiogram import Router
from . import menu, types, events, calendar


def setup_routers() -> Router:
    root = Router()
    root.include_router(menu.router)
    root.include_router(types.router)
    root.include_router(events.router)
    root.include_router(calendar.router)
    return root