import random
from datetime import datetime
from gm.api import *
from pandas import DataFrame

import pandas as pd
import src.configure.configure as configure
from enum import Enum
import mplfinance as mpf
from finta import TA

# 设置token， 查看已有token ID,在用户-密钥管理里获取
set_token(configure.token)
now = datetime.now()

# 创建一个字典，用于定义K线图的颜色
mc = mpf.make_marketcolors(up='r', down='g', inherit=True)
# 创建一个样式对象，用于定义K线图的样式
k_style = mpf.make_mpf_style(marketcolors=mc)


def color_ao(input_datas: DataFrame) -> [str]:
    ao_list = input_datas['ao']
    colors = ['r']
    for i in range(1, len(ao_list)):
        if ao_list[i] > ao_list[i - 1]:
            colors.append('r')
        elif ao_list[i] == ao_list[i - 1]:
            colors.append(colors[i - 1])
        else:
            colors.append('g')
    return colors


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
def get_n_price_before_now(symbol: str, frequency: Frequency, count: int) -> DataFrame:
    data = get_n_data_before_now(symbol, frequency, count)
    return data[['open', 'close', 'high', 'low']]


# 计算AO指标
# 最近5根平均移动值 - 最近34根平均移动值
def set_ao(data: DataFrame) -> DataFrame:
    # 计算AO指标
    data['ao'] = TA.AO(data)
    return data


def color_func(x):
    if x > 0:
        return 'g'
    else:
        return 'r'


# 绘制AO柱状图
def draw_kline_with_ao(data: DataFrame):
    set_ao(data)
    dates = pd.date_range(start='01-01-2020', periods=len(data))
    data.set_index(dates, inplace=True)
    # 创建一个figure
    fig = mpf.figure(style='yahoo', figsize=(7, 8))

    # 添加一个subplot用于绘制K线图
    ax1 = fig.add_subplot(2, 1, 1)
    mpf.plot(data, ax=ax1, type='candle', style=k_style)

    color_list = color_ao(data)
    # 添加一个subplot用于绘制AO指标图
    ax2 = fig.add_subplot(2, 1, 2)
    ax2.bar(data.index, data['ao'], alpha=0.7, color=color_list)

    # 显示图表
    mpf.show()


# 绘制k线图
def draw_k_line(data: DataFrame):
    # 绘制k线图
    dates = pd.date_range(start='01-01-2020', periods=len(data))
    data.set_index(dates, inplace=True)
    mpf.plot(data, type='candle', style=k_style)


def draw_3k_line(day: DataFrame, hour: DataFrame, quarter: DataFrame):
    fig = mpf.figure(style='yahoo', figsize=(7, 8))

    date_day = pd.date_range(start='01-01-2020', periods=len(day))
    day.set_index(date_day, inplace=True)
    ax1 = fig.add_subplot(3, 1, 1)
    mpf.plot(day, type='candle', ax=ax1, style=k_style)
    ax1.set_title('day')

    date_hour = pd.date_range(start='01-01-2020', periods=len(hour))
    hour.set_index(date_hour, inplace=True)
    ax2 = fig.add_subplot(3, 1, 2, sharex=ax1)
    mpf.plot(hour, type='candle', ax=ax2, style=k_style)
    ax2.set_title('hour')

    date_quarter = pd.date_range(start='01-01-2020', periods=len(quarter))
    quarter.set_index(date_quarter, inplace=True)
    ax3 = fig.add_subplot(3, 1, 3, sharex=ax1)
    mpf.plot(quarter, type='candle', ax=ax3, style=k_style)
    ax3.set_title('quarter')

    mpf.show()


def draw_alligator_line(day: DataFrame):
    dates = pd.date_range(start='01-01-2020', periods=len(day))
    day.set_index(dates, inplace=True)

    # 绘制鳄鱼线
    day['Mid'] = (day['high'] + day['low']) / 2

    # 计算鳄鱼的嘴巴、牙齿和嘴唇
    day['Jaw'] = day['Mid'].rolling(13).mean().shift(8)
    day['Teeth'] = day['Mid'].rolling(8).mean().shift(5)
    day['Lips'] = day['Mid'].rolling(5).mean().shift(3)

    # 计算AO指标
    set_ao(day)
    day = day.dropna()
    color_list = color_ao(day)
    # 创建附加的绘图用于绘制鳄鱼线和AO图
    ap = [mpf.make_addplot(day['Jaw'], panel=0, color='blue'),
          mpf.make_addplot(day['Teeth'], panel=0, color='red'),
          mpf.make_addplot(day['Lips'], panel=0, color='green'),
          mpf.make_addplot(day['ao'], panel=1, type='bar', color=color_list, secondary_y=False)]

    # 使用mpf.plot()函数来绘制K线图、鳄鱼线和AO图
    mpf.plot(day, type='candle', addplot=ap)


if __name__ == '__main__':
    d1 = get_n_price_before_now('SHSE.510300', Frequency.Frequency_H, 100)
    d2 = get_n_price_before_now('SHSE.510300', Frequency.Frequency_M, 100)
    d3 = get_n_price_before_now('SHSE.510300', Frequency.Frequency_L, 100)
    # draw_3k_line(d1, d2, d3)
    # draw_kline_with_ao(d4)
    draw_alligator_line(d1)
