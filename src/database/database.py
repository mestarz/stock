from datetime import datetime
from gm.api import *
from pandas import DataFrame

import pandas as pd
import src.configure.configure as configure
from enum import Enum
import mplfinance as mpl

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


# 获取开盘价、收盘价、最高价、最低价
def get_n_price_before_now(symbol: str, frequency: Frequency, count: int):
    data = get_n_data_before_now(symbol, frequency, count)
    return data[['open', 'close', 'high', 'low']]


# 绘制k线图
def draw_k_line(data: DataFrame):
    # 绘制k线图
    dates = pd.date_range(start='01-01-2020', periods=len(data))
    data.set_index(dates, inplace=True)
    mpl.plot(data, type='candle')


def draw_3k_line(day: DataFrame, hour: DataFrame, quarter: DataFrame):
    fig = mpl.figure(style='yahoo', figsize=(7, 8))

    date_day = pd.date_range(start='01-01-2020', periods=len(day))
    day.set_index(date_day, inplace=True)
    ax1 = fig.add_subplot(3, 1, 1)
    mpl.plot(day, type='candle', ax=ax1)
    ax1.set_title('day')

    date_hour = pd.date_range(start='01-01-2020', periods=len(hour))
    hour.set_index(date_hour, inplace=True)
    ax2 = fig.add_subplot(3, 1, 2, sharex=ax1)
    mpl.plot(hour, type='candle', ax=ax2)
    ax2.set_title('hour')

    date_quarter = pd.date_range(start='01-01-2020', periods=len(quarter))
    quarter.set_index(date_quarter, inplace=True)
    ax3 = fig.add_subplot(3, 1, 3, sharex=ax1)
    mpl.plot(quarter, type='candle', ax=ax3)
    ax3.set_title('quarter')

    mpl.show()


# 绘制鳄鱼线
def draw_alligator_line(day: DataFrame, hour: DataFrame, quarter: DataFrame):
    # 绘制鳄鱼线
    dates = pd.date_range(start='01-01-2020', periods=len(day))
    day.set_index(dates, inplace=True)
    hour.set_index(dates, inplace=True)
    quarter.set_index(dates, inplace=True)
    mpl.plot(day, type='candle')
    mpl.plot(hour, type='candle')
    mpl.plot(quarter, type='candle')


# 日k：14
# 小时k: 14 * 4 = 56
# 15mink： 14 * 4 * 4 = 224

if __name__ == '__main__':
    d1 = get_n_price_before_now('SHSE.510300', Frequency.Frequency_H, 100)
    d2 = get_n_price_before_now('SHSE.510300', Frequency.Frequency_M, 100)
    d3 = get_n_price_before_now('SHSE.510300', Frequency.Frequency_L, 100)
    draw_3k_line(d1, d2, d3)
