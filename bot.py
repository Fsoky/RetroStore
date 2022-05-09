from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from motor.motor_asyncio import AsyncIOMotorClient

import config

bot = Bot(config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

cluster = AsyncIOMotorClient(config.MONGO_TOKEN)
collection = cluster.tele_store.store


class StoreForm(StatesGroup):
    add_item_action = State()
    remove_item_action = State()
    buy_item_action = State()


@dp.message_handler(commands="add")
async def add_item(message: types.Message):
    await message.answer("Введите название предмета:")
    await StoreForm.add_item_action.set()


@dp.message_handler(state=StoreForm.add_item_action)
async def add_item_process(message: types.Message, state: FSMContext):
    await collection.update_one({"name": "RetroStore"},
        {"$push": {"items": message.text}})
    await state.finish()


@dp.message_handler(commands="remove")
async def remove_item(message: types.Message):
    await message.answer("Введите название предмета, чтобы удалить:")
    await StoreForm.remove_item_action.set()


@dp.message_handler(state=StoreForm.remove_item_action)
async def remove_item_process(message: types.Message, state: FSMContext):
    is_exists = await collection.count_documents({"name": "RetroStore",
        "items": message.text})
    if is_exists:
        await collection.update_one({"name": "RetroStore"},
            {"$pull": {"items": message.text}})
        await state.finish()
    else:
        await message.answer("Товара не существует...")

@dp.message_handler(commands="buy")
async def buy_item(message: types.Message):
    await message.answer("Введите название предмета, чтобы купить:")
    await StoreForm.buy_item_action.set()


@dp.message_handler(state=StoreForm.buy_item_action)
async def buy_item_process(message: types.Message, state=FSMContext):
    is_exists = await collection.count_documents({"name": "RetroStore",
        "items": message.text})
    if is_exists:
        await message.answer("Вы успешно приобрели товар.")
        # Если этот ролик наберет обороты, в следующем можно будет
        # реализовать аккаунты
    else:
        await message.answer("Товара не существует...")

    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

