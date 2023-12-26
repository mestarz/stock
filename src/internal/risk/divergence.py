import pandas as pd
import numpy as np
from pandas import DataFrame


# 做多背离柱风险, 当跌破30日内最底背离柱时，卖出，风险为True
def divergence_risk_up(df: DataFrame) -> bool:
    # 获取最近30日数据
    df = df[-30:]
    divergence_level1 = np.array(df['divergence level1'])

    # 从右往左找出最近的底背离柱
    index = -1
    for i in range(len(df) - 1, -1, -1):
        if divergence_level1[i] == -1:
            index = i
            break

    if index == -1:
        return False

    # 如果最近的底背离柱被下击穿，风险为True
    if df['low'].values[index] > min(df['low'].values):
        return True

    return False
