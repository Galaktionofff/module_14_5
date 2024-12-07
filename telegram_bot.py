import aiogram as ai
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio
import sqlite3
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from crud_functions import *

initiate_db()
initiate_users_db()

# for i in range(1, 4 + 1):
#     cursor.execute(" INSERT INTO Products(title, description, price) VALUES (?, ?, ?)",
#                    (f'банка{i}', f'{i} - хороша банка', i * 10))

api = '7514207461:AAGu7ivIl_q3aDoo9-HQeRZEklGmNYjblD8'
bot = ai.Bot(token=api)
dp = ai.Dispatcher(bot, storage=MemoryStorage())

"""Создание клавиатуры кнопок"""
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Информация')
button1 = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Купить')
button3 = KeyboardButton(text='Регистрация')
keyboard.row(button)
keyboard.row(button1)
keyboard.insert(button2)
keyboard.row(button3)
"""
keyboard.row - позволяет вставить блок кнопки в ряд 
keyboard.insert - вставляет блоки в нижние ряды до тех пор, пока они не заполнятся,
 в таком случае она перейдет на ряд выше 
 """
"""Создание инлайновых(внутри сообщений) кнопок"""
kb_il = InlineKeyboardMarkup()
Inline_button = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
Inline_button1 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb_il.add(Inline_button)
kb_il.add(Inline_button1)

kb_in = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Product1", callback_data="product_buying"),
         InlineKeyboardButton(text="Product2", callback_data="product_buying")],
        [InlineKeyboardButton(text="Product3", callback_data="product_buying"),
         InlineKeyboardButton(text="Product4", callback_data="product_buying")]
    ]
)

# """Другой способ создания клавиатуры кнопок"""
# start_menu = ReplyKeyboardMarkup(keyboard=[
#     [KeyboardButton(text='Info')],#Один список = один ряд
#     [
#         KeyboardButton(text='Shop'),#Два списка в одном ряду
#         KeyboardButton(text='Donat')
#     ]
# ])


"""Логика их работы"""


@dp.message_handler(commands=['start'])
async def start(message):
    print('Привет! Я бот помогающий твоему здоровью.')
    await message.answer('Привет!  Я бот помогающий твоему здоровью.', reply_markup=keyboard)


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию', reply_markup=kb_il)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('10 х вес (кг) + 6,25 х рост (см) - 5 х возраст (г) - 161')
    await call.answer()


"""Эта ^^^ строчка нужна, чтобы заканчивать вызов кнопки"""


@dp.message_handler(text='Информация')
async def info(message):
    await message.answer("Меня сделал Никитос")


"""Чтобы достать из отправленного боту сообщения текст нужно брать параметр текст
message.text"""


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()


@dp.message_handler(text='Регистрация')
async def sing_up(message):
    await message.answer(text="Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if is_included(message.text) is False:
        await state.update_data(username=message.text)
        await message.answer(text="Введите свой email")
        await RegistrationState.email.set()
    else:
        await message.answer(text="Пользователь существует, введите другое имя")
        await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await message.answer(text="Введите свой возраст:")
    await RegistrationState.age.set()


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    add_user(str(data['username']), str(data['email']), int(data['age']))
    await message.answer(text="Регистрация прошла успешно!")
    await state.finish()


class User_state(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст')
    await call.answer()
    await User_state.age.set()


@dp.message_handler(state=User_state.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост')
    await User_state.growth.set()


@dp.message_handler(state=User_state.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес')
    await User_state.weight.set()


@dp.message_handler(state=User_state.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    await message.answer(
        f'Ваша норма калорий {10 * int(data["weight"]) + 6.25 * int(data["growth"]) - 5 * int(data["age"])}')
    await state.finish()


@dp.message_handler(text="Купить")
async def get_buying_list(message):
    get_all = get_all_products()
    for i in range(0, 4):
        id, title, description, price = get_all[i]
        await message.answer(f'Название: {title} / Описание: {description} / Цена: {price}')
        with open(f'{i + 1}.jpg', 'rb') as img:
            await message.answer_photo(img)
    await message.answer(text="Выберете продукт для покупки", reply_markup=kb_in)


@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer(text="Вы успешно приобрели продукт!")
    await call.answer()


# @dp.message_handler()
# async def all_message(message):
#     print('Введите команду /start, чтобы начать общение.')
#     await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    ai.executor.start_polling(dp, skip_updates=True)
