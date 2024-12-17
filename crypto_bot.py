

from imports import *

dp = Dispatcher(storage=MemoryStorage())

class CryptoState(StatesGroup):
    crypto_currency = State()
    time_period = State()


class Volatility(StatesGroup):
    time_period = State()

# Обработка команды /start
@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer(f"Привет, {html.bold(message.from_user.full_name)}! Я криптовалютный бот.")
    await message.answer('Нажми кнопку "Обзор рынка", чтобы узнать ситуацию на рынке или "Волатильность", '
                         'чтобы узнать волатильность крупнейших криптовалют', reply_markup=kb)

#Машина состояний для обработки нажатия кнопки Машина состояний для нажатой кнопки «Обзор рынка». Последовательно
# выводятся меню, позволяющие выбрать анализируемые криптовалюту и временной период, которые передаются в функцию
# crypto_history, после чего текстовые сообщения, возвращённые данной функцией, а также сохранённый файл graph.png
# выводятся пользователю в виде нескольких отдельных сообщений.
@dp.message(F.text.lower() == 'обзор рынка')
async def set_cur(message: Message, state: FSMContext):
    await message.answer("Выберите криптовалюту", reply_markup=kb1)
    await state.set_state(CryptoState.crypto_currency)


@dp.message(F.text, CryptoState.crypto_currency)
async def set_time(message: Message, state: FSMContext):
    await state.update_data(crypto_currency=message.text)
    await message.answer("Выберите временной период", reply_markup=kb2)
    await state.set_state(CryptoState.time_period)

# Машина состояний для нажатой кнопки «Волатильность». Возникающее меню позволяет выбрать временной период для анализа,
# после чего он передаётся в функцию volatility, результат которой выводится пользователю в виде текстовых сообщений.
@dp.message(F.text, CryptoState.time_period)
async def send_review(message: Message, state: FSMContext):
    await state.update_data(time_period=message.text)
    await message.answer("Минутку, ваш запрос обрабатывается", reply_markup=ReplyKeyboardRemove())
    data = await state.get_data()
    symbol, period = data['crypto_currency'] + 'USDT', data['time_period']
    t_max, t_min, t_vol = crypto_history(symbol, period)
    await message.answer(t_max)
    await message.answer(t_min)
    await message.answer(t_vol)
    photo = FSInputFile('graph.png')
    await message.reply_photo(photo, reply_markup=kb)
    await state.clear()


@dp.message(F.text.lower() == 'волатильность')
async def review_volatility(message: Message, state: FSMContext):
    await message.answer("Выберите временной период", reply_markup=kb2)
    await state.set_state(Volatility.time_period)


@dp.message(F.text, Volatility.time_period)
async def send_volatility(message: Message, state: FSMContext):
    await state.update_data(time_period=message.text)
    await message.answer("Минутку, ваш запрос обрабатывается", reply_markup=ReplyKeyboardRemove())
    data = await state.get_data()
    period = data['time_period']
    v_max, v_min = volatility(period)
    await message.answer(v_max)
    await message.answer(v_min, reply_markup=kb)
    await state.clear()


#Обработка текстовых сообщений "стоп" и "stop", если пользователь хочет остановить работу бота.
@dp.message(or_f(F.text.lower() == 'стоп', F.text.lower() == 'stop'))
async def ending(message: Message):
    await message.answer("Бот выключен")
    await sys.exit(0)


#Обработка любой команды, которая неизвестна боту.
@dp.message()
async def default_answer(message: Message):
    await message.answer('Введите команду /start, чтобы начать общение.')


async def main():
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()