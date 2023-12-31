from datetime import datetime

import pandas
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


# 获取当前的基本面数据，包括市盈率、市净率、市销率、市现率、总市值、当日换手率
def get_n_fundamental_before_now(symbols: [str]) -> DataFrame:
    def get_info(syms: [str]) -> DataFrame:
        return get_fundamentals(table='tq_sk_finindic', symbols=syms, start_date=now, end_date=now,
                                fields="PETTM, PB, PSTTM, PCTTM, TOTMKTCAP, TURNRATE", df=True)

    # 每100个股票一次请求
    step = 50
    data = get_info(symbols[:step])
    data.set_index('symbol', inplace=True)
    if len(symbols) > step:
        for i in range(step, len(symbols), step):
            new_data = get_info(symbols[i:i + step])
            new_data.set_index('symbol', inplace=True)
            data = pandas.concat([data, new_data])
    return data


# 获取A股股票, 返回字典
# 获取各个行业股票信息
# SHSE.000985	中证全指, all
# SHSE.000986	全指能源, energy
# SHSE.000987	全指材料, material
# SHSE.000988	全指工业, industry
# SHSE.000989	全指可选, optional
# SHSE.000990	全指消费, consumption
# SHSE.000991	全指医药, medicine
# SHSE.000992	全指金融, finance
# SHSE.000993	全指信息, information
# SHSE.000994	全指电信, telecom
# SHSE.000995	全指公用, public
# 参考：https://emquant.18.cn/help/doc/data/data_index.html
def get_all_stocks() -> dict[str, []]:
    def get_stocks_list(index: str) -> []:
        return get_constituents(index, fields=None, df=True)['symbol'].tolist()

    result = dict()
    result['all'] = get_stocks_list("SHSE.000985")
    result['energy'] = get_stocks_list("SHSE.000986")
    result['material'] = get_stocks_list("SHSE.000987")
    result['industry'] = get_stocks_list("SHSE.000988")
    result['optional'] = get_stocks_list("SHSE.000989")
    result['consumption'] = get_stocks_list("SHSE.000990")
    result['medicine'] = get_stocks_list("SHSE.000991")
    result['finance'] = get_stocks_list("SHSE.000992")
    result['information'] = get_stocks_list("SHSE.000993")
    result['telecom'] = get_stocks_list("SHSE.000994")
    result['public'] = get_stocks_list("SHSE.000995")
    return result


# 获取可转债数据
if __name__ == '__main__':
    # infos = get_all_stocks()
    # print(infos)
    infos = get_n_fundamental_before_now(['SZSE.002923', 'SHSE.603826'])
    print(infos)
