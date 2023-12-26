from pandas import DataFrame
import numpy as np
from finta import TA


# 获取上一次与鳄鱼线相交的价格柱下标
def get_last_intersect_index(data: DataFrame, index: int) -> int:
    while index >= 0:
        if (data['low'][index] <= data['jaw'][index] <= data['high'][index]) or (
                data['low'][index] <= data['teeth'][index] <= data['high'][index]) or (
                data['low'][index] <= data['lips'][index] <= data['high'][index]):
            break
        index -= 1
    return index


# 分析数据，获取顶背离柱和底背离柱
# 返回一个与输入数据等长的数组，数组中的元素为0表示没有背离柱，为1表示顶背离柱，为-1表示底背离柱
def analyse_divergence(data: DataFrame) -> None:
    # 获取开盘价、收盘价、最高价、最低价
    open_list = data['open']
    close_list = data['close']
    high_list = data['high']
    low_list = data['low']

    # 一级背离
    # 顶背离，最高点处于阶段高点，当然收盘价小于开盘价，收盘价在价格柱下半部分，同时保证价格柱远离鳄鱼线
    # 底背离，最低点处于阶段低点，当然收盘价大于开盘价，收盘价在价格柱上半部分，同时保证价格柱远离鳄鱼线
    divergence_level1 = [0] * len(data)
    for i in range(1, len(data)):
        # 找寻阶段点，上一次与鳄鱼线相交的价格柱下标
        index = get_last_intersect_index(data, i - 1)
        if index < 0:
            index = 0
        # 获取阶段最高点，最低点
        max_price = max(high_list[index:i].values)
        min_price = min(low_list[index:i].values)
        # 如果是顶背离
        if high_list[i] > max_price and \
                open_list[i] > close_list[i] and \
                low_list[i] > data['jaw'][i] and \
                low_list[i] > data['teeth'][i] and \
                low_list[i] > data['lips'][i] and \
                close_list[i] < (high_list[i] + low_list[i]) / 2:
            divergence_level1[i] = -1
        # 如果是底背离
        elif low_list[i] < min_price and \
                open_list[i] < close_list[i] and \
                high_list[i] < data['jaw'][i] and \
                high_list[i] < data['teeth'][i] and \
                high_list[i] < data['lips'][i] and \
                close_list[i] > (high_list[i] + low_list[i]) / 2:
            divergence_level1[i] = 1
    data['divergence level1'] = divergence_level1

    # 二级背离
    # 顶背离，最高点大于前高，当然收盘价小于开盘价，同时保证价格柱远离鳄鱼线
    # 底背离，最低点小于前低，当然收盘价大于开盘价，同时保证价格柱远离鳄鱼线
    divergence_level2 = [0] * len(data)
    for i in range(1, len(data)):
        # 如果是顶背离
        if high_list[i] > high_list[i - 1] and \
                open_list[i] > close_list[i] and \
                low_list[i] > data['jaw'][i] and \
                low_list[i] > data['teeth'][i] and \
                low_list[i] > data['lips'][i]:
            divergence_level2[i] = -1
        # 如果是底背离
        elif low_list[i] < low_list[i - 1] and \
                open_list[i] < close_list[i] and \
                high_list[i] < data['jaw'][i] and \
                high_list[i] < data['teeth'][i] and \
                high_list[i] < data['lips'][i]:
            divergence_level2[i] = 1
    data['divergence level2'] = divergence_level2

    # 计算发散夹角用于辅助背离柱指标，只有当角度大于0时，才是有效背离柱
    # 定义一个函数来计算趋势线的斜率
    def trend_slope(series):
        return np.polyfit(range(len(series)), series, 1)[0]

    angle = [0] * len(data)
    # 遍历每一根K线
    for i in range(len(data)):
        # 找出上一次与鳄鱼线相交的价格柱下标
        index = get_last_intersect_index(data, i - 1)
        if index < 0:
            continue

        # 计算鳄鱼线趋势斜率, 计算点data['jaw'][index]和data['teeth'][i]的斜率
        jaw_slope = (data['jaw'][i] - data['jaw'][index]) / (i - index)
        # 计算价格趋势斜率, 上升趋势中，根据最高点拟合斜率；下降趋势中，根据最低点拟合斜率
        if data['close'][i] > data['close'][index]:
            price_slope = trend_slope(data['high'][index:i + 1].values)
        else:
            price_slope = trend_slope(data['low'][index:i + 1].values)

        # 斜率标准化, 正常来说价格越高斜率越大，所以根据当前价格标准斜率
        # 以价格10为基数进行格式
        price_slope = (price_slope / data['close'][i]) * 10
        jaw_slope = (jaw_slope / data['close'][i]) * 10

        # 计算0到x方向的发散夹角, 收敛夹角无效
        # 上升趋势，价格斜率大于鳄鱼线斜率
        if price_slope > jaw_slope and data['close'][i] > data['close'][index]:
            angle[i] = np.arctan(
                abs((price_slope - jaw_slope) / (1 + price_slope * jaw_slope))) * 180 / np.pi
        # 下降趋势，价格斜率小于鳄鱼线斜率
        elif price_slope < jaw_slope and data['close'][i] < data['close'][index]:
            angle[i] = np.arctan(
                abs((jaw_slope - price_slope) / (1 + jaw_slope * price_slope))) * 180 / np.pi

    data['angle'] = angle


# 计算AO指标
# 最近5根平均移动值 - 最近34根平均移动值
def analyse_ao(data: DataFrame) -> None:
    # 计算AO指标
    data['ao'] = TA.AO(data)


# 计算鳄鱼线
def analyse_alligator_line(data: DataFrame) -> None:
    # 计算鳄鱼的嘴巴、牙齿和嘴唇
    data['mid'] = (data['high'] + data['low']) / 2
    data['jaw'] = data['mid'].rolling(13).mean().shift(8)
    data['teeth'] = data['mid'].rolling(8).mean().shift(5)
    data['lips'] = data['mid'].rolling(5).mean().shift(3)


# 判断是否是上分型
# 输入 [1*5] 的数据, 返回bool值
def is_up_fractal(data: DataFrame) -> bool:
    # 判断是否是上分型, 5根K线中，中间一根最高，两边都比它低
    if data['high'].values[2] == max(data['high'].values):
        return True
    return False


# 判断是否是下分型
# 输入 [1*5] 的数据, 返回bool值
def is_down_fractal(data: DataFrame) -> bool:
    # 判断是否是下分型, 5根K线中，中间一根最低，两边都比它高
    if data['low'].values[2] == min(data['low'].values):
        return True
    return False


# 分析分型数据
def analyse_fractal(data: DataFrame) -> None:
    # 分析上分型
    up_fractal = [0] * len(data)
    for i in range(2, len(data) - 2):
        if is_up_fractal(data[i - 2:i + 3]):
            up_fractal[i] = 1
    data['up fractal'] = up_fractal

    # 分析下分型
    down_fractal = [0] * len(data)
    for i in range(2, len(data) - 2):
        if is_down_fractal(data[i - 2:i + 3]):
            down_fractal[i] = 1
    data['down fractal'] = down_fractal


# 计算每日的历史波动率
def analyse_volatility(data: DataFrame) -> None:
    # 计算每日收益率
    data['daily return'] = data['close'].pct_change()
    # 计算每日波动率, 波动率的精度为小数点后两位，周期为28天
    data['volatility'] = data['daily return'].rolling(28).std() * np.sqrt(28).round(2)