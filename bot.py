from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from avito_parser import get_content, read_db, write_db
from urllib.parse import urlparse
import logging
import asyncio
import config
import json

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

data = read_db()


class Dialog(StatesGroup):
    waiting_for_interval_time = State()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\n"
                        "Отправь мне ссылку на подборку товаров авито и я каждые 5 минут буду проверять "
                        "новые объявления!")


@dp.message_handler(commands=['interval'])
async def process_interval_command(message: types.Message):
    await message.answer("С каким минутным интервалом хочешь получать новые объявления? (По умолчанию - 5 минут)")
    await Dialog.waiting_for_interval_time.set()


@dp.message_handler(state=Dialog.waiting_for_interval_time)
async def interval(message: types.Message, state: FSMContext):
    time = message.text
    json_data = read_db()
    json_data["interval"] = int(time) * 60
    write_db(json_data)
    await message.answer(f"Хорошо, теперь объявленя будут присылаться с интервалом в {time} минут")
    await state.finish()


@dp.message_handler(commands=['stop'])
async def process_start_command(message: types.Message):
    data["URL"] = ""
    write_db(data)
    await message.reply("Поиск товаров по этой ссылке остановлен.\n Отправь новую ссылку!")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Отправь команду /stop, если хочешь остановить получения объявлений.\n"
                        "Отправь команду /interval, если хочешь изменить интервал получения новых объявлений")


@dp.message_handler()
async def start(messsage: types.Message):
    data["ID"] = str(messsage.chat.id)

    if urlparse(messsage.text).netloc == 'www.avito.ru':
        data["URL"] = str(messsage.text)
        data["products"] = []
        write_db(data)
        await post_send()
    else:
        await bot.send_message(data['ID'], 'Неверный запрос, укажите ссылку на товары авито')


@dp.message_handler()
async def post_send():
    while True:
        if data["URL"] == "":
            break
        try:
            posts = get_content(data["URL"])
            if len(posts) != 0:
                for post in posts:
                    await bot.send_photo(data['ID'], post['image'],
                                         caption=post['title'] + "\n" + "Цена: " + post['price']
                                                 + "\n" + post['geo'] + "\n\n" + post['link'])
                    await asyncio.sleep(3)
        except TypeError:
            await bot.send_message(data['ID'], 'Некорректная ссылка')
            break
        await asyncio.sleep(data['interval'])


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
