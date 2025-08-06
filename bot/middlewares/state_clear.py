from aiogram import BaseMiddleware, types
from aiogram.fsm.context import FSMContext


class StateClearMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: types.Message, data: dict):
        state: FSMContext = data.get("state")
        if event.text and event.text.startswith("/"):
            if data:
                await state.clear()
        return await handler(event, data)
