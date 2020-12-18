import config
import logging
from aiogram import Bot, Dispatcher, executor, types
import asyncio
from avito_parser import get_content
from urllib.parse import urlparse
import json

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

with open("db.json", "r") as jsonFile:
    data = json.load(jsonFile)
    jsonFile.close()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\n"
                        "Отправь мне ссылку на подборку товаров авито и я буду присылать тебе новые объявления!")


@dp.message_handler(commands=['stop'])
async def process_start_command(message: types.Message):
    data["URL"] = ""
    with open("db.json", "w") as file:
        json.dump(data, file, indent=4)
        file.close()
    await message.reply("Поиск товаров по этой ссылке остановлен.\n Отправь новую ссылку!")


@dp.message_handler()
async def start(messsage: types.Message):
    data["ID"] = str(messsage.chat.id)

    if urlparse(messsage.text).netloc == 'www.avito.ru':
        data["URL"] = str(messsage.text)
        data["products"] = []
        with open("db.json", "w") as file:
            json.dump(data, file, indent=4)
            file.close()
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
        except TypeError:
            await bot.send_message(data['ID'], 'Некорректная ссылка')
            break
        await asyncio.sleep(10)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
