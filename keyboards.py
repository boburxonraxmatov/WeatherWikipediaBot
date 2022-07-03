from aiogram import types


def start_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(text='Weather')
    btn2 = types.KeyboardButton(text='Wikipedia')
    markup.add(*[btn1, btn2])
    return markup

