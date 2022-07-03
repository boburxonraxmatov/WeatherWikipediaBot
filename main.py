import sqlite3
from datetime import datetime

import requests
import wikipedia as wikipedia
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage  # Хранилице в памяти, куда будем сохранять
from aiogram.dispatcher import FSMContext  # Адрес на локальное хранилище - Оперативка
from aiogram.dispatcher.filters.state import State, StatesGroup  # Группа вопросов и вопросы
from aiogram.types import Message

from configs import *
# import psycopg2
from keyboards import start_markup

storage = MemoryStorage()  # Открываем хранилице
bot = Bot(token=TOKEN, parse_mode='HTML')  # Подключитесь к боту в телеграме, и редактирование в виде HTML

dp = Dispatcher(bot, storage=storage)  # Объект диспейчера, который будет следить за ботом, сохраняем хранилице

wikipedia.set_lang('ru')


class GetWeather(StatesGroup):
    city = State()


class GetAction(StatesGroup):
    action = State()


class GetQuestions(StatesGroup):
    ques = State()


@dp.message_handler(commands=['start', 'about', 'help'])  # , 'about', 'help'
async def command_start(message: Message):
    if message.text == '/start':
        await message.answer(f'Здравствуйте <b>{message.from_user.full_name}</b>. Я бот и я хочу угодить вам',
                             reply_markup=start_markup())
        await get_action(message)
    elif message.text == '/about':
        await message.answer(f'''Данный бот был создын в <i>домашних условиях</i>''')
    elif message.text == '/help':
        await message.answer(
            '''При возникших идеях или проблемах пишите сюда: <tg-spoiler>@boburxon_raxmatov</tg-spoiler>''')


async def get_first_city(message: Message):
    await GetWeather.city.set()
    await message.answer('Введите город у которого хотите узнать погоду: ')


async def get_action(message: Message):
    await GetAction.action.set()
    await message.answer('Выберите действия: ')


async def get_first_question(message: Message):
    await GetQuestions.ques.set()
    await bot.send_message(message.chat.id, 'Введите вопрос на который хотите узнать ответ: ')


@dp.message_handler(state=GetAction.action)
async def process_action(message: Message, state: FSMContext):
    if message.text.lower() == "Weather".lower():
        await get_first_city(message)
    elif message.text.lower() == "Wikipedia".lower():
        await get_first_question(message)


@dp.message_handler(state=GetWeather.city)
async def show_city_weather(message: Message, state: FSMContext):
    # await bot.send_message(message.chat.id, f"{message.text}")
    try:
        parameters['q'] = message.text

        data = requests.get('https://api.openweathermap.org/data/2.5/weather', params=parameters).json()
        temp = data['main']['temp']
        wind = data['wind']['speed']
        name = data['name']
        description = data['weather'][0]['description']
        timezone = data['timezone']
        sunrise = datetime.utcfromtimestamp(data['sys']['sunrise'] + timezone).strftime('%H:%M:%S')  # %Y:%M:%D
        sunset = datetime.utcfromtimestamp(data['sys']['sunset'] + timezone).strftime('%H:%M:%S')
        await bot.send_message(message.chat.id, f'''В городе {name} сейчас {description}
Температура: {temp} °C
Скорость ветра: {wind} м/с
Рассвет: {sunrise} часов
Закат: {sunset} часов''')

        database = sqlite3.connect('ls5.db')
        cursor = database.cursor()
        cursor.execute('''
            INSERT INTO weather(temp, wind, name, description, sunrise, sunset)
            VALUES (?,?,?,?,?,?);
            ''', (temp, wind, name, description, sunrise, sunset))
        database.commit()
        database.close()
        await state.finish()
        await bot.send_message(message.chat.id, f"""Выбери команду
/start
/about
/help
""")

    except Exception as e:
        print(e)
        await bot.send_message(message.chat.id, 'Не верно указан город, Попробуй снова!!!')
        await get_first_city(message)


@dp.message_handler(state=GetQuestions.ques)
async def show_questions(message: Message, state: FSMContext):
    python_page = wikipedia.page(message.text)
    print(python_page.url)
    try:
        await message.reply(f'''
HTML страницы: {python_page.url}
Заголовок статьи: {python_page.original_title}
{python_page.summary}
''')

        # Создание файла
        with open('text.txt', 'a', encoding='UTF-8') as file:
            file.write(python_page.original_title + '\n')  # Заполняем текстовый файл # Парсится заголовок
            file.write(python_page.summary + '\n')  # Парсится краткое содержание
            file.write('Ссылка на источник: ' + python_page.url + '\n')

        await state.finish()

    except Exception as e:
        print(e)
        await bot.send_message(message.chat.id, 'Введите вопрос точнее!!!')
        await get_first_question(message)


executor.start_polling(dp)
