from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

button1 = KeyboardButton(text='Обзор рынка')
button2 = KeyboardButton(text='Волатильность')
kb = ReplyKeyboardMarkup(keyboard=[[button1, button2]], resize_keyboard=True)

button1_1 = KeyboardButton(text='BTC', callback_data='BTC')
button1_2 = KeyboardButton(text='ETH', callback_data='ETH')
button1_3 = KeyboardButton(text='TON', callback_data='TON')
button1_4 = KeyboardButton(text='SOL', callback_data='SOL')
kb1 = ReplyKeyboardMarkup(keyboard=[[button1_1, button1_2, button1_3, button1_4]], resize_keyboard=True)

button2_1 = KeyboardButton(text='1m', callback_data='1m')
button2_2 = KeyboardButton(text='5m', callback_data='5m')
button2_3 = KeyboardButton(text='1h', callback_data='1h')
button2_4 = KeyboardButton(text='1d', callback_data='1d')
kb2 = ReplyKeyboardMarkup(keyboard=[[button2_1, button2_2, button2_3, button2_4]], resize_keyboard=True)
