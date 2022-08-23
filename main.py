import ast
import logging
from random import randint

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

m_id = None
raitings = None
API_TOKEN = 'TOKEN'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


def writerating(r):
    data = open("raiting.txt", "w")
    data.write(str(r))
    data.close()


def readrating():
    global raitings
    data = open("raiting.txt", "r")
    raitings = ast.literal_eval(data.read())
    data.close()
    return raitings


@dp.callback_query_handler(text="home")
async def home(call: types.CallbackQuery):
    global m_id
    await start(call.message)


@dp.callback_query_handler(text="exit")
async def exit_bot(call: types.CallbackQuery):
    await bot.delete_message(message_id=call.message.message_id, chat_id=call.message.chat.id)
    global m_id
    m_id = None


@dp.message_handler(Text('@justacoldbot'))
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user = message.from_user.username
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    markup.add(InlineKeyboardButton(text='Камень, ножницы, бумага 🗿✂📑', callback_data="RPS"))
    markup.add(InlineKeyboardButton(text='Посмотеть рейтинг📈', callback_data="raiting"))
    markup.add(InlineKeyboardButton(text='Выйти из бота❌', callback_data="exit"))
    a = await message.answer(f'Здравствуйте, <b>{user}</b>\n\nЧто Вам хотелось бы сделать?', reply_markup=markup)
    global m_id
    if m_id:
        await bot.delete_message(message_id=m_id, chat_id=message.chat.id)
    m_id = a.message_id


@dp.callback_query_handler(text="raiting")
async def send_random_value(call: types.CallbackQuery):
    readrating()
    user = call.from_user.username
    text = 'Камень ножницы бумага| <b>' + str(raitings['RPS'][str(user)]) + '</b>'
    await call.message.answer(f'Рейтинг <b>{user}📈\n{text}</b>')
    global m_id
    if m_id:
        await bot.delete_message(message_id=m_id, chat_id=call.message.chat.id)
    m_id = None
    await bot.delete_message(message_id=call.message.message_id, chat_id=call.message.chat.id)
    await exit_bot(call)


@dp.callback_query_handler(text="RPS")
async def send_random_value(call: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    markup.add(InlineKeyboardButton(text='Камень 🗿', callback_data="RPS_1"))
    markup.add(InlineKeyboardButton(text='Ножницы ✂', callback_data="RPS_2"))
    markup.add(InlineKeyboardButton(text='Бумага 📑', callback_data="RPS_3"))
    a = await call.message.answer('Как ходите?', reply_markup=markup)
    global m_id
    if m_id:
        await bot.delete_message(message_id=m_id, chat_id=call.message.chat.id)
    m_id = a.message_id


@dp.callback_query_handler(text_contains="RPS_")
async def send_random_value(call: types.CallbackQuery):
    readrating()
    global raitings
    variants = {1: 'Камень', 2: 'Ножницы', 3: 'Бумага'}
    user = call.from_user.username
    bot_choice = randint(1, 3)
    user_choice = int(call.data[-1])
    text = 'Ошибка'
    if user not in raitings['RPS']:
        raitings['RPS'][user] = 0
    if user_choice == bot_choice + 1 or user_choice == bot_choice - 2:
        raitings['RPS'][user] -= 1
        text = "🤖<b>Бот</b> победил"
    elif user_choice == bot_choice - 1 or user_choice == bot_choice + 2:
        raitings['RPS'][user] += 1
        text = f"😌<b>{user}</b> победил"
    else:
        text = "😐<b>Ничья</b>"
    writerating(raitings)
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    await call.message.answer(
        f'{user} выбрал <b>{variants[user_choice]}</b>, бот выбрал <b>{variants[bot_choice]}</b>\n<i>{text}</i>')
    markup.add(InlineKeyboardButton(text=f'Новая игра🎲', callback_data="RPS"))
    markup.add(InlineKeyboardButton(text=f'На главную🏚', callback_data="home"))
    a = await call.message.answer('Начать заново?', reply_markup=markup)
    global m_id
    if m_id:
        await bot.delete_message(message_id=m_id, chat_id=call.message.chat.id)
    m_id = a.message_id


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
