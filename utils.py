from enum import Enum

from datetime import datetime
import random
import pandas as pd
import os
from gm.api import *
import configure

# 可以直接提取数据，东方财富量化终端需要打开，接口取数是通过网络请求的方式，效率一般，行情数据可通过subscribe订阅方式
# 设置token， 查看已有token ID,在用户-密钥管理里获取
set_token(configure.token)
now = datetime.now()
g_symbols: [str] = []


class Frequency(Enum):
    Frequency_Day = '1d'
    Frequency_Hour = '1h'
    Frequency_Minute = '60s'


class CoreSymbol(Enum):
    沪深300ETF_159919 = 'SZSE.159919'
    创业板ETF_159915 = 'SZSE.159915'
    深证100ETF_159901 = 'SZSE.159901'
    中证500ETF_159922 = 'SZSE.159922'
    沪深300ETF_510300 = 'SHSE.510300'
    中证500ETF_510500 = 'SHSE.510500'
    上证50ETF_510050 = 'SHSE.510050'
    科创版50ETF_588080 = 'SHSE.588080'
    科创50ETF_588000 = 'SHSE.588000'


def get_data(symbol: str, frequency: Frequency, start: datetime, end: datetime):
    start_time = start.strftime("%Y-%m-%d %H:%M:%S")
    end_time = end.strftime("%Y-%m-%d %H:%M:%S")
    data = history(symbol=symbol, frequency=frequency.value, start_time=start_time,
                   end_time=end_time,
                   adjust=ADJUST_PREV, df=True)
    return data


def get_data_n(symbol: str, frequency: Frequency, count: int, end: datetime):
    end_time = end.strftime("%Y-%m-%d %H:%M:%S")
    data = history_n(symbol=symbol, frequency=frequency.value, count=count,
                     end_time=end_time,
                     adjust=ADJUST_PREV, df=True)
    return data


def get_all_symbol() -> [str]:
    global g_symbols
    if len(g_symbols) > 0:
        return g_symbols

    file_path = os.path.join(os.path.dirname(__file__), './data/symbol.data')
    df = pd.read_csv(file_path)
    g_symbols = df.values.flatten()
    return g_symbols


def get_random_symbol(num: int) -> [str]:
    datas = get_all_symbol()
    index = random.sample(range(len(datas)), num)
    return [datas[i] for i in index]


def is_valid_symbol(symbol: str) -> bool:
    symbols = get_all_symbol()
    if symbol in symbols:
        return True
    date = get_data_n(symbol, Frequency.Frequency_Day, 1, now)
    if date.size > 0:
        return True
    return False
