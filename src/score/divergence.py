from pandas import DataFrame
import numpy as np
from src.database.database import get_n_price_before_now, Frequency
from src.draw import draw


# 根据三日内是否出现背离线计算做多得分
def divergence_score_up(df: DataFrame) -> float:
    score = 0.0

    # 获取最近三日数据
    df = df[-3:]
    divergence_level1 = np.array(df['divergence level1'])
    divergence_level2 = np.array(df['divergence level2'])
    angle = np.array(df['angle'])

    # 过滤出底背离, 将等于-1的值替换为0
    divergence_level1[divergence_level1 == -1] = 0
    divergence_level2[divergence_level2 == -1] = 0

    # 如果底背离被下击穿，无效
    for i in range(len(df)):
        if df['low'].values[i] > min(df['low'].values):
            divergence_level1[i] = 0
            divergence_level2[i] = 0

    # 最近三日内是否出现底背离线, 一级底背离
    # 得分计算 权重 * 夹角, 三日权重[1, 2, 4]
    divergence_level1_angle = divergence_level1 * angle
    score += sum(divergence_level1_angle * [1, 2, 4])

    # 三日内是否出现底背离线, 二级底背离
    # 得分计算 权重 * 夹角, 三日权重[1, 2, 4] * 0.5
    divergence_level2_angle = divergence_level2 * angle
    score += sum(divergence_level2_angle * [1, 2, 4] * 0.5)

    return score


# 根据三日内是否出现顶背离线计算做空得分
def divergence_score_down(df: DataFrame) -> float:
    score = 0.0

    # 获取最近三日数据
    df = df[-3:]
    divergence_level1 = np.array(df['divergence level1'])
    divergence_level2 = np.array(df['divergence level2'])
    angle = np.array(df['angle'])

    # 过滤出顶背离, 将等于1的值替换为0
    divergence_level1[divergence_level1 == 1] = 0
    divergence_level2[divergence_level2 == 1] = 0

    # 如果顶背离被上击穿，无效
    for i in range(len(df)):
        if df['high'].values[i] < max(df['high'].values):
            divergence_level1[i] = 0
            divergence_level2[i] = 0

    # 最近三日内是否出现底背离线, 一级底背离
    # 得分计算 权重 * 夹角, 三日权重[1, 2, 4]
    divergence_level1_angle = divergence_level1 * angle
    score += sum(divergence_level1_angle * [1, 2, 4])

    # 三日内是否出现底背离线, 二级底背离
    # 得分计算 权重 * 夹角, 三日权重[1, 2, 4] * 0.5
    divergence_level2_angle = divergence_level2 * angle
    score += sum(divergence_level2_angle * [1, 2, 4] * 0.5)

    # 三日得分求和
    return score


if __name__ == '__main__':
    d1 = get_n_price_before_now('SZSE.300939', Frequency.Frequency_H, 50)
    score_up = divergence_score_up(d1)
    score_down = divergence_score_down(d1)
    print(score_up)
    print(score_down)
