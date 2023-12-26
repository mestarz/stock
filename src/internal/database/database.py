from datetime import datetime
from gm.api import *
from pandas import DataFrame

import src.internal.data.configure as configure
from enum import Enum

from src.internal.database.analyse import analyse_divergence, analyse_ao, analyse_alligator_line, analyse_fractal, \
    analyse_volatility

# 设置token， 查看已有token ID,在用户-密钥管理里获取
set_token(configure.token)
now = datetime.now()


class Frequency(Enum):
    Frequency_H = '1d'
    Frequency_M = '1h'
    Frequency_L = '900s'


def get_n_data_before_now(symbol: str, frequency: Frequency, count: int) -> DataFrame:
    end_time = now.strftime("%Y-%m-%d %H:%M:%S")
    data = history_n(symbol=symbol, frequency=frequency.value, count=count,
                     end_time=end_time,
                     adjust=ADJUST_PREV, df=True)
    return data


# 获取开盘价、收盘价、最高价、最低价、AO指标、鳄鱼线的嘴巴、牙齿和嘴唇
def get_n_price_before_now(symbol: str, frequency: Frequency, count: int) -> DataFrame:
    data = get_n_data_before_now(symbol, frequency, count)
    data = data[['open', 'close', 'high', 'low']]

    # 计算鳄鱼的嘴巴、牙齿和嘴唇
    analyse_alligator_line(data)
    # 计算AO指标
    analyse_ao(data)
    # 计算背离柱
    analyse_divergence(data)
    # 分析分型数据
    analyse_fractal(data)
    # 分析波动率
    analyse_volatility(data)

    return data
