from binance.client import Client
import pandas as pd
import matplotlib.pyplot as plt
from threading import Thread

period_dic = {'1m': '1 минута', '5m': '5 минут', '30m': '30 минут', '1h': '1 час',
              '4h': '4 часа', '1d': '1 день'}

# Функция get_data(symbol, period) делает запрос к криптобирже Binance по открытому API, помещая результат запроса в
# датафрейм, после чего оставляет в таблице только шесть столбцов, представляющих интерес, забирая данные со второй
# строки. Последующие строки кода переводят столбец Time в миллисекунды, а столбцы High и Low в тип данных float.
# Затем функция возвращает обработанный датафрейм.
# По умолчанию функция принимает аргументами биткойн и период 1 час.

def get_data(symbol='BTCUSDT', period='1h'):
    client = Client()
    df = pd.DataFrame(client.get_historical_klines(symbol, period, ))
    df = df.iloc[1:, :6]
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    df['Time'] = pd.to_datetime(df['Time'], unit='ms')
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    return df

# Функция crypto_history при помощи функции get_data получает данные о необходимой криптовалюте, после чего записывает
# в переменные максимальное значение из столбца max и минимальное значение из столбца min, а также значения времени из
# столбца Time , в которое были достигнуты соответствующие пики.

def crypto_history(symbol, period):
    df = get_data(symbol, period)
    high_value = max(df['High'])
    low_value = min(df['Low'])
    high_time = df.loc[df['High'] == high_value]['Time'].values[0]
    low_time = df.loc[df['Low'] == low_value]['Time'].values[0]

# Далее готовятся текстовые сообщения с рассчитанными данными, которые позднее функция вернёт для отправки
# пользователю.

    begin_phrase = f'Криптовалюта {symbol.rstrip("USDT")} за последние тысячу периодов "{period_dic[period]}" достигала'
    t_max = begin_phrase + f' максимума {high_value:.2f}. Это было {str(high_time)[:10]} в {str(high_time)[11:16]}'
    t_min = begin_phrase + f' минимума {low_value:.2f}. Это было {str(low_time)[:10]} в {str(low_time)[11:16]}'
    t_vol = f'Волатильность составила: {(high_value - low_value) / low_value * 100:.2f}%'

# После этого строится график стоимости запрошенной криптовалюты по значению из столбца Close, после чего график
# сохраняется во временный файл graph.png, а функция возвращает подготовленные текстовые сообщения.

    x = df['Time']
    y = df['Close'].astype(float)
    plt.figure(figsize=(10, 5))
    plt.plot(x, y, 'g')
    plt.axhline(y=high_value, color='g', linestyle='--')
    plt.axhline(y=low_value, color='r', linestyle='--')
    plt.xlabel('Даты')
    plt.ylabel('Стоимость в USD')
    plt.title(f'График стоимости {symbol} с {str(df['Time'].iloc[0])[:16]} по {str(df['Time'].iloc[-1])[:16]}')
    plt.tick_params(axis='x', labelrotation=90)
    plt.tight_layout()
    plt.savefig('graph.png')
    return t_max, t_min, t_vol

# Функция volatility принимает наименование временного интервала, а возвращает две переменных с текстовым описанием
# наиболее и наименее волатильных криптовалют.
# Сначала функция создаёт пустой словарь, в который будут заноситься значения волатильности,
# после чего в списке перечисляются 10 основных криптовалют.

def volatility(period):
    vol = dict()
    currencies = ['_BTC', '_ETH', '_XRP', '_DOGE', '_SOL', '_AVAX', '_TON', '_BNB', '_ADA', '_TRX']

# Далее создаётся функция process_request, которая рассчитывает волатильность одной конкретной криптовалюты и
# помещает полученные данные в словарь.

    def process_request(self, *c):
        symbol = ''.join(c) + 'USDT'
        df = get_data(symbol, period)
        high_value = max(df['High'])
        low_value = min(df['Low'])
        vol[symbol] = (high_value - low_value) / low_value * 100

# Далее создаётся отдельный поток для каждой из криптовалют списка currencies, чтобы запросы к серверу биржи могли
# осуществляться параллельно. Потоки заносятся в список, запускаются, после чего второй цикл ожидает завершения их
# работы.

    threads = []
    for c in currencies:
        threads.append(Thread(target=process_request, args=c, daemon=True))
        threads[-1].start()
    for t in threads:
        t.join()

#После этого словарь преобразуется в список кортежей, сортируется, а крайние значения используются для создания
# текстовых ответов пользователю, которые возвращает функция.

    vol = sorted(list(vol.items()), key=lambda item: item[1])
    v_max = (f'Максимальная волатильность за последние тысячу периодов "{period_dic[period]}" '
             f'наблюдалась у криптовалюты {vol[-1][0]} и составила {vol[-1][1]:.2f}%')
    v_min = (f'Минимальная волатильность за последние тысячу периодов "{period_dic[period]}" '
             f'наблюдалась у криптовалюты {vol[0][0]} и составила {vol[0][1]:.2f}%')
    return v_max, v_min