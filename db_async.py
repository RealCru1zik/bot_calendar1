import asyncio
from functools import partial
from typing import Any, Callable

from db import (
    init_db, list_types, get_type, add_type, delete_type,
    list_responsibles, add_responsible,
    add_event, get_event, list_all_events,
    list_events_for_day, count_events_by_day, delete_event,
)


async def run(func: Callable, *args, **kwargs) -> Any:
    return await asyncio.to_thread(partial(func, *args, **kwargs))


# Прокси-функции, чтобы в хендлерах писать db.list_types() и не думать
async def a_init_db():
    return await run(init_db)

async def a_list_types():
    return await run(list_types)

async def a_get_type(type_id: int):
    return await run(get_type, type_id)

async def a_add_type(name: str):
    return await run(add_type, name)

async def a_delete_type(name: str):
    return await run(delete_type, name)

async def a_list_responsibles():
    return await run(list_responsibles)

async def a_add_responsible(name: str):
    return await run(add_responsible, name)

async def a_add_event(**kwargs):
    return await run(add_event, **kwargs)

async def a_get_event(event_id: int):
    return await run(get_event, event_id)

async def a_list_all_events():
    return await run(list_all_events)

async def a_list_events_for_day(date_str: str):
    return await run(list_events_for_day, date_str)

async def a_count_events_by_day(start_date: str, end_date: str):
    return await run(count_events_by_day, start_date, end_date)

async def a_delete_event(event_id: int):
    return await run(delete_event, event_id)