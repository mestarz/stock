from datetime import datetime
from gm.api import *
from pandas import DataFrame
import src.draw.draw as draw

import src.configure.configure as configure
from enum import Enum

from src.database.analyse import analyse_divergence, analyse_ao, analyse_alligator_line, analyse_fractal

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

    return data


if __name__ == '__main__':
    d1 = get_n_price_before_now('SHSE.510300', Frequency.Frequency_H, 300)
    d2 = get_n_price_before_now('SHSE.510300', Frequency.Frequency_M, 100)
    d3 = get_n_price_before_now('SHSE.510300', Frequency.Frequency_L, 100)
    # analyse_divergence(d1)
    # print(d1['angle'])
    # print(d1['divergence'])
    # print(d1['angle'][50:])
    draw.draw_alligator_line(d1)
    # print(d1['valid divergence'][50:])
