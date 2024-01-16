from pandas import DataFrame
import numpy as np
from src.internal.score.score import ScorePass, LimitPass


# 计算鳄鱼线排列得分, 以鳄鱼线的排列方向为准，如果鳄鱼线向上排列，做多得分为1，做空得分为0，反之亦然
class AlligatorLine(ScorePass):

    def __init__(self, score_weight: float = 1):
        super().__init__(score_weight=score_weight)

    @staticmethod
    # 判断n日内鳄鱼线交叉程度，如果鳄鱼线三线排列相互交叉程度越高，得分越低
    def cross(df: DataFrame, day_num=14) -> float:
        # 单日交叉程度计算
        def crossing_one_day(jaw: float, teeth: float, lips: float) -> float:
            return abs(jaw - teeth) + abs(teeth - lips) + abs(jaw - lips)

        df = df[-day_num:]
        # 计算交叉程度的标准差， 标准差越高，交叉程度越高，得分越低
        cross_list = [crossing_one_day(df['jaw'].values[i], df['teeth'].values[i], df['lips'].values[i]) for i in
                      range(day_num)]

        # 计算标准差
        std = np.std(cross_list)

        # 标准差越高，交叉程度越高，得分越低
        # std -> +inf, score -> 0
        # std -> 0, score -> 1
        return 1 / (1 + std)

    @staticmethod
    # 判断鳄鱼线趋势，返回三线斜率的平均值
    def trend(df: DataFrame, day_num=14) -> float:
        # 计算斜率
        jaw_slope = np.polyfit(range(day_num), df['jaw'].values[-day_num:], 1)[0]
        teeth_slope = np.polyfit(range(day_num), df['teeth'].values[-day_num:], 1)[0]
        lips_slope = np.polyfit(range(day_num), df['lips'].values[-day_num:], 1)[0]

        # 返回三线斜率的平均值
        return (jaw_slope + teeth_slope + lips_slope) / 3

    # 做多得分
    def run_up(self, df: DataFrame) -> float:
        return self.trend(df) * self.cross(df)

    def run_down(self, df: DataFrame) -> float:
        return -self.trend(df) * self.cross(df)


# 第一内买卖点，n日内出现背离柱
class FirstInnerBuySellPoint(ScorePass):

    # day_num: 计算区间
    # day_weight: 区间内的每日权重
    # level2_wight: 二级背离权重
    def __init__(self, day_num: int = 3, day_weight: [] = None, level2_wight: float = 0.1, score_weight: float = 1):
        super().__init__(score_weight=score_weight)
        # 计算区间
        self.day_num = day_num
        # 设置权重
        if day_weight is None:
            # 如果权重未设置，以 [1, 2, 4, 8 ...]的序列设置权重
            self.day_weight = np.array([2 ** i for i in range(day_num)])
        else:
            assert len(day_weight) == day_num
            # 如果权重设置，使用设置的权重
            self.day_weight = np.array(day_weight)
        self.level2_wight = level2_wight

    # 根据n日内是否出现背离线计算做多得分
    def run_up(self, df: DataFrame) -> float:
        score = 0.0

        # 获取最近n数据
        assert len(df) >= self.day_num
        df = df[-self.day_num:]
        divergence_level1 = np.array(df['divergence level1'].values)
        divergence_level2 = np.array(df['divergence level2'].values)
        angle = np.array(df['angle'].values)

        # 过滤掉顶背离, 将等于-1的值替换为0
        divergence_level1[divergence_level1 == -1] = 0
        divergence_level2[divergence_level2 == -1] = 0

        # 如果底背离被下击穿，无效
        for i in range(len(df)):
            if df['low'].values[i] > min(df['low'].values):
                divergence_level1[i] = 0
                divergence_level2[i] = 0

        # 最近三日内是否出现底背离线, 一级底背离
        # 得分计算 权重 * 夹角
        divergence_level1_angle = divergence_level1 * angle
        score += sum(divergence_level1_angle * self.day_weight)

        # 三日内是否出现底背离线, 二级底背离
        # 得分计算 权重 * 夹角
        divergence_level2_angle = divergence_level2 * angle
        score += sum(divergence_level2_angle * self.day_weight * self.level2_wight)

        return score

    # 根据n日内是否出现背离线计算做空得分
    def run_down(self, df: DataFrame) -> float:
        score = 0.0

        # 获取最近n日数据
        assert len(df) >= self.day_num
        df = df[-self.day_num:]
        divergence_level1 = np.array(df['divergence level1'].values)
        divergence_level2 = np.array(df['divergence level2'].values)
        angle = np.array(df['angle'].values)

        # 过滤掉底背离, 将等于1的值替换为0
        divergence_level1[divergence_level1 == 1] = 0
        divergence_level2[divergence_level2 == 1] = 0

        # 如果顶背离被上击穿，无效
        for i in range(len(df)):
            if df['high'].values[i] < max(df['high'].values):
                divergence_level1[i] = 0
                divergence_level2[i] = 0

        # 最近三日内是否出现底背离线, 一级底背离
        # 得分计算 权重 * 夹角
        divergence_level1_angle = divergence_level1 * angle
        score += sum(divergence_level1_angle * self.day_weight)

        # 三日内是否出现底背离线, 二级底背离
        # 得分计算 权重 * 夹角
        divergence_level2_angle = divergence_level2 * angle
        score += sum(divergence_level2_angle * self.day_weight * self.level2_wight)

        # 三日得分求和
        return score


# 第二内买卖点，n日内出线背离柱，且AO动量递增
class SecondInnerBuySellPoint(ScorePass):

    # day_num: 计算区间
    # level2_wight: 二级背离权重
    def __init__(self, day_num: int = 3, level2_wight: float = 0.5, score_weight: float = 1):
        super().__init__(score_weight=score_weight)
        # 计算区间
        self.day_num = day_num
        # 设置权重
        self.level2_wight = level2_wight

    # n日内出现底背离柱, 该底部背离柱未被跌破，之后的近三日出现AO动量连续递增
    def run_up(self, df: DataFrame) -> float:
        score = 0.0

        # 获取最近n日数据
        assert len(df) >= self.day_num
        df = df[-self.day_num:]
        divergence_level1 = np.array(df['divergence level1'].values)
        divergence_level2 = np.array(df['divergence level2'].values)
        angle = np.array(df['angle'].values)
        ao = np.array(df['ao'].values)

        # 找到最近的底背离柱, 且有效的底背离柱
        # 当底背离柱在计算区间内，且未被跌破时，有效
        def get_divergence_index(level: np.array) -> int:
            for i in range(len(level)):
                if level[i] == 1 and df['low'].values[i] <= min(df['low'].values):
                    return i
            return -1

        # 近三日内，AO动量是否递增
        def ao_increase() -> int:
            for i in range(len(df) - 1, len(df) - 4, -1):
                if ao[i] < ao[i - 1]:
                    return 0
            return 1

        # 得分: (一级背离柱 * 一级背离柱夹角 +  二级背离柱 * 二级背离柱夹角 * 二级背离柱权重)  * AO动量是否递增
        index1 = get_divergence_index(divergence_level1)
        index2 = get_divergence_index(divergence_level2)
        return (divergence_level1[index1] * angle[index1] + divergence_level2[index2] * angle[
            index2] * self.level2_wight) * ao_increase()

    # n日内出现顶背离柱, 该顶部背离柱未被上穿，之后的近三日出现AO动量连续递减
    def run_down(self, df: DataFrame) -> float:
        score = 0.0

        # 获取最近n日数据
        assert len(df) >= self.day_num
        df = df[-self.day_num:]
        divergence_level1 = np.array(df['divergence level1'].values)
        divergence_level2 = np.array(df['divergence level2'].values)
        angle = np.array(df['angle'].values)
        ao = np.array(df['ao'].values)

        # 找到最近的顶背离柱, 且有效的顶背离柱
        # 当顶背离柱在计算区间内，且未被上穿时，有效
        def get_divergence_index(level: np.array) -> int:
            for i in range(len(level)):
                if level[i] == -1 and df['high'].values[i] > max(df['high'].values):
                    return i
            return -1

        # 近三日内，AO动量是否递减
        def ao_decrease() -> int:
            for i in range(len(df) - 1, len(df) - 4, -1):
                if ao[i] > ao[i - 1]:
                    return 0
            return 1

        # 得分: (一级背离柱 * 一级背离柱夹角 +  二级背离柱 * 二级背离柱夹角 * 二级背离柱权重)  * AO动量是否递减
        index1 = get_divergence_index(divergence_level1)
        index2 = get_divergence_index(divergence_level2)
        return (divergence_level1[index1] * angle[index1] + divergence_level2[index2] * angle[
            index2] * self.level2_wight) * ao_decrease()


# 第三内买点，分型突破
class ThirdInnerBuySellPoint(ScorePass):

    def __init__(self, day_num: int = 30, score_weight: float = 1):
        super().__init__(score_weight=score_weight)
        self.day_num = day_num
        self.score_weight = 1

    #  day_num内是否出现分型突破, 第一次上分型的顶点突破鳄鱼线，第二次上分型顶点突破第一次上分型顶点
    def run_up(self, df: DataFrame) -> float:
        # 获取最近day_num数据
        assert len(df) >= self.day_num
        df = df[-self.day_num:]

        # 获取上分型数据
        up_fractal = np.array(df['up fractal'].values)

        # 获取三日内最近的上分型，如果没有，返回0
        this_index = -1
        for i in range(len(up_fractal) - 1, len(up_fractal) - 4, -1):
            if up_fractal[i] == 1:
                this_index = i
                break
        if this_index == -1:
            return 0

        # 获取index之前的突破鳄鱼线的最近上分型
        last = this_index
        for i in range(this_index - 1, -1, -1):
            high = df['high'].values[i]
            if up_fractal[i] == 1 and high > df['jaw'].values[i] and high > df['teeth'].values[i] and high > \
                    df['lips'].values[i]:
                last = i
                break
        if last == this_index:
            return 0

        # 最高点是否突破
        if df['high'].values[this_index] > df['high'].values[last]:
            return 1
        return 0

    # day_num内是否出现分型突破, 第一次下分型的底点突破鳄鱼线，第二次下分型底点突破第一次下分型底点
    def run_down(self, df: DataFrame) -> float:
        # 获取最近day_num数据
        assert len(df) >= self.day_num
        df = df[-self.day_num:]

        # 获取下分型数据
        down_fractal = np.array(df['down fractal'].values)

        # 获取三日内最近的下分型，如果没有，返回0
        this_index = -1
        for i in range(len(down_fractal) - 1, len(down_fractal) - 4, -1):
            if down_fractal[i] == 1:
                this_index = i
                break
        if this_index == -1:
            return 0

        # 获取index之前的突破鳄鱼线的最近下分型
        last = this_index
        for i in range(this_index - 1, -1, -1):
            low = df['low'].values[i]
            if down_fractal[i] == 1 and low < df['jaw'].values[i] and low < df['teeth'].values[i] and low < \
                    df['lips'].values[i]:
                last = i
                break
        if last == this_index:
            return 0

        # 最低点是否突破
        if df['low'].values[this_index] < df['low'].values[last]:
            return 1
        return 0


class StockFluctuateLimit(LimitPass):

    def run_up(self, df: DataFrame) -> bool:
        # 最近3天波动过大，超过10%
        assert len(df) >= 3
        min5day = df['low'].values[-3:].min()
        max5day = df['high'].values[-3].max()
        if (max5day - min5day) / min5day > 0.1:
            return False

        # 最近30日内波动过大，超过30%
        assert len(df) >= 30
        min30day = df['low'].values[-30:].min()
        max30day = df['high'].values[-30:].max()
        if (max30day - min30day) / min30day > 0.3:
            return False

    def run_down(self, df: DataFrame) -> bool:
        # 最近3天波动过大，超过10%
        assert len(df) >= 3
        min5day = df['low'].values[-3:].min()
        max5day = df['high'].values[-3].max()
        if (max5day - min5day) / min5day > 0.1:
            return False

        # 最近30日内波动过大，超过30%
        assert len(df) >= 30
        min30day = df['low'].values[-30:].min()
        max30day = df['high'].values[-30:].max()
        if (max30day - min30day) / min30day > 0.3:
            return False


class ChaosLimit(LimitPass):

    def run_up(self, df: DataFrame) -> bool:
        # 做多背离柱风险, 当跌破30日内最底背离柱时，卖出，返回False
        # 获取最近30日数据
        df = df[-30:]
        divergence_level1 = np.array(df['divergence level1'])
        # 从右往左找出最近的底背离柱
        index = -1
        for i in range(len(df) - 1, -1, -1):
            if divergence_level1[i] == -1:
                index = i
                break
        # 如果最近的底背离柱在之后被下击穿，存在风险
        if index != -1 and df['low'].values[index] > min(df['low'].values[index:]):
            return False
        return True

    def run_down(self, df: DataFrame) -> bool:
        # 做空背离柱风险, 当突破30日内最高背离柱时，卖出，返回False
        # 获取最近30日数据
        df = df[-30:]
        divergence_level1 = np.array(df['divergence level1'])
        # 从右往左找出最近的顶背离柱
        index = -1
        for i in range(len(df) - 1, -1, -1):
            if divergence_level1[i] == 1:
                index = i
                break
        # 如果最近的顶背离柱被上击穿，存在风险
        if index != -1 and df['high'].values[index] < max(df['high'].values[index:]):
            return False
        return True


# 基本面分析
# 小市值，低价股, 低市净率, 低市盈率
class FundamentalLimit(LimitPass):

    def run_up(self, df: DataFrame) -> bool:
        # 过滤掉价格高于price_limit的股票
        # price_limit = 50
        # if df['close'].values[-1] > price_limit:
        #     return False

        # 基本面分析, pe, pb, ps, pc, market_cap, turn_rate
        # 过滤掉市值大的股票, 100亿以下
        # market_cap = df['mark_cap'].values[-1]
        # if market_cap > 1e+10:
        #     return False
        # 过滤掉市盈率高的股票
        pe = df['pe'].values[-1]
        if pe > 40 or pe < 0:
            return False
        # 过滤掉市净率高的股票
        pb = df['pb'].values[-1]
        if pb > 3:
            return False
        return True

    def run_down(self, df: DataFrame) -> bool:
        return True
