import logging
from aiogram import Bot, Dispatcher, types, executor
import config
from filters import IsAdminFilter
import bad_words
from aiogram.contrib.fsm_storage.redis import RedisStorage
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from wait import WaitState
from aiogram.dispatcher import FSMContext


logging.basicConfig(level=logging.INFO)
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
storage = RedisStorage(host='localhost', port=6379)
dp.filters_factory.bind(IsAdminFilter)

@dp.message_handler(commands=['find'])
async def find_film_by_keyword(message: types.Message):
    await message.reply("Введите номер код фильма:")
    await WaitState.WAIT_KEYWORD.set()

@dp.message_handler(state=WaitState.WAIT_KEYWORD)
async def search_films(message: types.Message, state: FSMContext):
    keyword = message.text.strip().lower()
    found_films = []
    with open('films.txt', 'r', encoding='utf-8') as file:
        for line in file:
            if keyword in line.lower():
                found_films.append(line.strip())

    if found_films:
        films_list = '\n'.join(found_films)
        await message.reply(f"Найденный фильм:\n{films_list}")
    else:
        await message.reply("По вашему запросу ничего не найдено.")
    await state.finish()

@dp.message_handler(commands=['start'])
async def list_film(message: types.Message):
    await message.reply('Приветствуем тебя в нашем сообществе\n Список всех доступных команд можешь посмотреть с помощью команды /help')

@dp.message_handler(is_admin=True, commands=['list_film'])
async def list_film(message: types.Message):
    with open('films.txt', 'r', encoding='utf-8') as file:
        list = file.read()
    await message.reply(list)

@dp.message_handler(is_admin=True, commands=['admin'])
async def admin( message: types.Message):
    await message.reply('/list_film - список всех фильмов(admin)\n/film - добавление нового фильма(admin)\n/find - поиск фильма по коду')
@dp.message_handler( commands=['help'])
async def help( message: types.Message):
    await message.reply('find - поиск фильма по коду')

@dp.message_handler(is_admin=True, commands=['film'])
async def add_film(message: types.Message):
    await message.reply("Введите номер фильма:")
    await WaitState.WAIT_NUMBER.set()

@dp.message_handler(state=WaitState.WAIT_NUMBER)
async def save_number(message: types.Message, state: FSMContext):
    await state.update_data(number=message.text.strip())
    await message.reply("Введите название фильма:")
    await WaitState.WAIT_FILM.set()
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

@dp.message_handler(state=WaitState.WAIT_FILM)
async def save_film(message: types.Message, state: FSMContext):
    data = await state.get_data()
    number = data.get('number')
    film = message.text.strip()
    with open('films.txt', 'a', encoding='utf-8') as file:
        file.write(f"Номер: {number}, Фильм: {film}\n")
    await message.reply('Фильм успешно сохранен')
    await state.finish()

@dp.message_handler(is_admin=True, commands=['ban'], commands_prefix="!/" )
async def ban_comand(message: types.Message):
    try:
        if not message.reply_to_message:
            await message.reply('выбери пользователя!')
            return
        user_id = message.reply_to_message.from_user.id
        await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await message.bot.kick_chat_member(chat_id=message.chat.id, user_id=user_id)
        await message.reply_to_message.reply('Пользователь забанен')
    except Exception:
        await message.reply_to_message.reply('Нельзя забанить админа!')

@dp.message_handler()
async def filter_message(message: types.Message):
    for i in bad_words.bad:
        if i.lower() in message.text.lower():
            await message.delete()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
