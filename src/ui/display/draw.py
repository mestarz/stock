import mplfinance as mpf
from pandas import DataFrame
import pandas as pd

from src.internal.database.database import get_n_price_before_now, Frequency

# 创建一个字典，用于定义K线图的颜色
mc = mpf.make_marketcolors(up='r', down='g', inherit=True)
# 创建一个样式对象，用于定义K线图的样式
k_style = mpf.make_mpf_style(marketcolors=mc)


def color_func(x):
    if x > 0:
        return 'g'
    else:
        return 'r'


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


# 绘制AO柱状图
def draw_kline_with_ao(data: DataFrame):
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


def draw_alligator_line(day: DataFrame):
    dates = pd.date_range(start='01-01-2020', periods=len(day))
    day.set_index(dates, inplace=True)

    day = day.dropna()
    color_list = color_ao(day)
    # 创建附加的绘图用于绘制鳄鱼线和AO图
    ap = [mpf.make_addplot(day['jaw'], panel=0, color='blue'),
          mpf.make_addplot(day['teeth'], panel=0, color='red'),
          mpf.make_addplot(day['lips'], panel=0, color='green'),
          mpf.make_addplot(day['ao'], panel=1, type='bar', color=color_list, secondary_y=False),
          mpf.make_addplot(day['divergence level1'] * day['angle'], panel=2, type='bar', color='orange',
                           secondary_y=False),
          mpf.make_addplot(day['divergence level2'] * day['angle'], panel=3, type='bar', color='blue',
                           secondary_y=False),
          # 上分型数据
          mpf.make_addplot(day['up fractal'] * day['high'], panel=4, type='bar', color='red', markersize=100),
          # 下分型数据
          mpf.make_addplot(day['down fractal'] * day['low'], panel=5, type='bar', color='green', markersize=100),
          # 波动率数据
          mpf.make_addplot(day['volatility'], panel=6, type='bar', color='blue', secondary_y=False),
          ]

    # 获取所有 day['divergence level1'] * day['angle'] != 0 的下标
    index_list = day[(day['divergence level1'] * day['angle'] != 0)].index.tolist()

    # 使用mpf.plot()函数来绘制K线图、鳄鱼线和AO图
    mpf.plot(day, type='candle', addplot=ap,
             vlines=dict(vlines=index_list, linewidths=[0.1] * len(index_list),
                         colors=['orange'] * len(index_list),
                         linestyle='dashed', alpha=0.3))


if __name__ == '__main__':
    d1 = get_n_price_before_now('SHSE.603136', Frequency.Frequency_H, 300)
    d2 = get_n_price_before_now('SHSE.510300', Frequency.Frequency_M, 100)
    d3 = get_n_price_before_now('SHSE.510300', Frequency.Frequency_L, 100)
    draw_alligator_line(d1)
