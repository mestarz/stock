from src.internal.score.score import ScorePass, LimitPass
from pandas import DataFrame


# 可转债四因子策略
# 1. 低价策略
# 2. 低溢价策略
# 3. 低流通盘 - 暂不支持
# 4. 高换手率 - 暂不支持
class CBFourFactors(ScorePass):

    def __init__(self, score_weight: float = 1):
        super().__init__(score_weight=score_weight)

    def run_up(self, df) -> float:
        score = 0
        # 价格低于price_limit时，增加做多得分, 价格越低，做多得分越高
        price_limit = 100
        current_price = df['close'].values[-1]
        if current_price < price_limit:
            score += super().normalization((price_limit - current_price) * 0.1)

        # 转股溢价越低，做多得分越高
        # 转股溢价低于conversion_premium时，增加做多得分, 转股溢价越低，做多得分越高
        conversion_premium = df['conversion_premium'].values[-1]
        price_limit = 0
        if conversion_premium < price_limit:
            score += super().normalization((price_limit - conversion_premium) * 100)

        return score

    def run_down(self, df) -> float:
        score = 0
        # 价格超过price_limit时，增加做空得分, 价格越高，做空得分越高
        price_limit = 110
        current_price = df['close'].values[-1]
        if current_price > price_limit:
            score += super().normalization((current_price - price_limit) * 0.1)

        # 转股溢价越高，做空得分越高
        # 转股溢价高于premium_limit时，增加做空得分, 转股溢价越高，做空得分越高
        premium_limit = 0
        conversion_premium = df['conversion_premium'].values[-1]
        if conversion_premium > premium_limit:
            score += super().normalization((conversion_premium - premium_limit) * 100)

        return score


class CBondLimit(LimitPass):

    def run_up(self, df: DataFrame) -> bool:

        # 债券价格过高
        current_price = df['close'].values[-1]
        if current_price > 120:
            return False

        # 最近5天波动过大，超过10%, 仅限制高价格债券
        assert len(df) >= 6
        min5day = df['low'].values[-6:].min()
        max5day = df['high'].values[-6:].max()
        if (max5day - min5day) / min5day > 0.1 and current_price > 110:
            return False

        # 近日波动过大，超过3%, 仅限制高价格债券
        assert len(df) >= 2
        min2day = df['low'].values[-2:].min()
        max2day = df['high'].values[-2:].max()
        if (max2day - min2day) / min2day > 0.03 and current_price > 110:
            return False

        # 转股溢价过高
        premium = df['conversion_premium'].values[-1]
        price = df['close'].values[-1]
        if price < 90:
            return premium < 0.8
        elif price < 100:
            return premium < 0.5
        elif price < 120:
            return premium < 0.2
        else:
            return premium < 0.1

    def run_down(self, df: DataFrame) -> bool:
        return True
