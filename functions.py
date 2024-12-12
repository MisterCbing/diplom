# Для работы пакета требуется установленный модуль python-binance.
import io
from binance.client import Client
import pandas as pd
import matplotlib.pyplot as plt
from threading import Thread

period_dic = {'1m': '1 минута', '5m': '5 минут', '30m': '30 минут', '1h': '1 час',
              '4h': '4 часа', '1d': '1 день'}


def get_data(symbol='BTCUSDT', period='1h'):
    client = Client()
    df = pd.DataFrame(client.get_historical_klines(symbol, period, ))
    df = df.iloc[1:, :6]
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    df['Time'] = pd.to_datetime(df['Time'], unit='ms')
    df['High'] = df['High'].astype(float)
    df['Low'] = df['Low'].astype(float)
    return df


# Функция crypto_history анализирует поведение криптовалюты на бирже Binance за последние тысячу временных отрезков.
# Функция принимает два аргумента - тикер криптовалюты и наименование временного интервала. В коде прописаны шесть
# вариантов интервалов, которые являются наиболее распространёнными: 1m, 5m, 30m, 1h, 4h, 1d.
# По умолчанию функция принимает аргументами биткойн и период 1 час.
# Обращаясь к бирже, функция получает необходимые данные, переводит их в dataframe и обрабатывает.
# Результатом работы функции является вывод текстовой информации о максимальном и минимальном значениях указанной
# криптовалюты в изучаемом периоде; времени и дате, когда были достигнуты эти пиковые значения; волатильности
# криптовалюты за указанный период.
# После двухсекундной задержки за выводом текстовой информации выводится график движения стоимости криптовалюты в
# исследуемом периоде. Зелёной пунктирной линией отмечен максимум, красной пунктирной линией - минимум.
# Чтобы даты на оси x не накладывались друг на друга они развёрнуты на 90 градусов с помощью labelrotation, а чтобы
# они поместились на изображении использован метод tight_layout.
def crypto_history(symbol, period):
    df = get_data(symbol, period)
    high_value = max(df['High'])
    low_value = min(df['Low'])
    high_time = df.loc[df['High'] == high_value]['Time'].values[0]
    low_time = df.loc[df['Low'] == low_value]['Time'].values[0]

    begin_phrase = f'Криптовалюта {symbol.rstrip("USDT")} за последние тысячу периодов "{period_dic[period]}" достигала'
    t_max = begin_phrase + f' максимума {high_value:.2f}. Это было {str(high_time)[:10]} в {str(high_time)[11:16]}'
    t_min = begin_phrase + f' минимума {low_value:.2f}. Это было {str(low_time)[:10]} в {str(low_time)[11:16]}'
    t_vol = f'Волатильность составила: {(high_value - low_value) / low_value * 100:.2f}%'

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


def volatility(period):
    vol = dict()
    currencies = ['_BTC', '_ETH', '_XRP', '_DOGE', '_SOL', '_AVAX', '_TON', '_BNB', '_ADA', '_TRX']

    def process_request(self, *c):
        symbol = ''.join(c) + 'USDT'
        df = get_data(symbol, period)
        high_value = max(df['High'])
        low_value = min(df['Low'])
        vol[symbol] = (high_value - low_value) / low_value * 100

    threads = []
    for c in currencies:
        threads.append(Thread(target=process_request, args=c, daemon=True))
        threads[-1].start()
    for t in threads:
        t.join()

    vol = sorted(list(vol.items()), key=lambda item: item[1])
    v_max = (f'Максимальная волатильность за последние тысячу периодов "{period_dic[period]}" '
             f'наблюдалась у криптовалюты {vol[-1][0]} и составила {vol[-1][1]:.2f}%')
    v_min = (f'Минимальная волатильность за последние тысячу периодов "{period_dic[period]}" '
             f'наблюдалась у криптовалюты {vol[0][0]} и составила {vol[0][1]:.2f}%')
    return v_max, v_min
