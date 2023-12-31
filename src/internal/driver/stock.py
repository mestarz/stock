import os

from src.internal.database.database import get_n_price_before_now, Frequency, get_all_stocks, \
    get_n_fundamental_before_now
import src.internal.score.score as score
import src.internal.score.chaos_operations as chaos_operations
from pandas import DataFrame


# 设置基本面信息
def set_fundamental(symbol: str, df: DataFrame, fundamentals: DataFrame):
    # 根据symbol找到对应的基本面信息
    info = fundamentals.loc[symbol]
    # 设置市盈率
    df['pe'] = [info['PETTM']] * len(df)
    # 设置市净率
    df['pb'] = [info['PB']] * len(df)
    # 设置市销率
    df['ps'] = [info['PSTTM']] * len(df)
    # 设置市现率
    df['pcf'] = [info['PCTTM']] * len(df)
    # 设置总市值
    df['mark_cap'] = [info['TOTMKTCAP']] * len(df)
    # 设置当日换手率
    df['turn_rate'] = [info['TURNRATE']] * len(df)
    return df


# 获取全部股票,根据divergence_score_up和divergence_score_down计算得分，将得分写入到data/score.data文件中
# data/score.data文件中的数据格式为：股票代码,做多得分,做空得分,波动率得分
def analyse_divergence_score():
    # 获取项目根目录
    root_path = os.path.dirname(os.path.dirname(__file__))

    # 读取股票代码
    symbol_list = get_all_stocks()['all'][:100]

    # 获取基本面信息
    fundamentals = get_n_fundamental_before_now(symbol_list)

    # 构造得分系统
    # score
    score_manager = score.ScorePassManager()
    score_manager.add_score_pass(chaos_operations.AlligatorLine(4))
    score_manager.add_score_pass(chaos_operations.FirstInnerBuySellPoint(1))
    score_manager.add_score_pass(chaos_operations.SecondInnerBuySellPoint(2))
    score_manager.add_score_pass(chaos_operations.ThirdInnerBuySellPoint(4))
    score_manager.add_score_pass(chaos_operations.ChaosLimit())
    score_manager.add_score_pass(chaos_operations.FundamentalLimit())

    # 遍历所有股票代码，计算得分
    with open(os.path.join(root_path, 'data/score.data'), 'w') as f:
        for symbol in symbol_list:
            # 获取最近300日的数据
            df = get_n_price_before_now(symbol, Frequency.Frequency_H, 60)
            # 设置基本面信息,市盈率、市净率、市销率、市现率、总市值、当日换手率
            df = set_fundamental(symbol, df, fundamentals)
            # 计算做多得分
            score_up = score_manager.run_up(df)
            # 计算做空得分
            score_down = score_manager.run_down(df)
            # 计算波动率得分
            score_volatility = df['volatility'].values[-1]
            # 将得分写入文件
            f.write(symbol + ',' + str(score_up) + ',' + str(score_down) + ',' + str(score_volatility) + '\n')


# 读取data/score.data文件中的数据，根据做多得分进行排序，选取前n个股票，作为返回值
def get_topn_score_up(n: int = 100) -> [[]]:
    # 获取项目根目录
    root_path = os.path.dirname(os.path.dirname(__file__))

    # 读取股票代码
    with open(os.path.join(root_path, 'data/score.data'), 'r') as f:
        score_list = f.read().splitlines()

    # 过滤掉做多得分为-inf的股票
    score_list = [x for x in score_list if float(x.split(',')[1]) != -float('inf')]

    def get_score(x):
        # 做空得分<0时，返回做多得分
        if float(x.split(',')[2]) < 0:
            return float(x.split(',')[1])
        # 做空得分>0时，返回做多得分-做空得分
        return float(x.split(',')[1]) - float(x.split(',')[2])

    # 根据做多得分进行排序
    score_list.sort(key=lambda x: float(get_score(x)), reverse=True)

    # 选取前100个股票
    score_list = score_list[:n]
    score_list = [x.split(',') for x in score_list]
    return score_list


# 根据波动率计算每个股票占比，波动率越高占比越低，总占比为1
# 输出是股票代码和占比的字典
# 输入是列表[[股票代码,做多得分,做空得分,波动率得分],...]
def get_weight_by_volatility(data: []):
    # 波动率越大，得分越低
    # ratio -> +inf, score -> 0
    # ratio -> 0, score -> 1
    volatility = [float(x[3]) for x in data]
    max_volatility = max(volatility)

    # 曲线经过点(0,1)和(2max_volatility,0)
    # y = x^2 + bx + 1
    # 0 = (2max_volatility)^2 + b(2max_volatility) + 1
    # b = -4max_volatility - 1 / (2max_volatility)
    b = -4 * max_volatility - 1 / (2 * max_volatility)

    # 计算每个股票的波动率得分
    reciprocals = [x * x + b * x + 1 for x in volatility]

    # 计算波动率倒数总和
    sum_reciprocal = sum(reciprocals)
    # 计算每个股票的占比
    weight_list = [x / sum_reciprocal for x in reciprocals]
    # 构建字典
    weight_dict = {}
    for i in range(len(data)):
        weight_dict[data[i][0]] = weight_list[i]

    # 根据占比进行排序
    weight_dict = dict(sorted(weight_dict.items(), key=lambda x: x[1], reverse=True))

    return weight_dict


# 将股票代码及占比导出到data/output_stock.txt文件中
def output(datas: [[]]):
    # 计算波动率
    weight_dict = get_weight_by_volatility(datas)
    # 将[股票代码,占比]写入文件data/output_stock.txt中
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/output_stock.txt'), 'w') as f:
        for key in weight_dict.keys():
            f.write(key + ',' + str(weight_dict[key]) + '\n')
    # 同时将data/output_stock.txt拷贝到桌面
    os.system('cp ' + os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/output_stock.txt') + ' ~/Desktop')


if __name__ == '__main__':
    analyse_divergence_score()
    scores = get_topn_score_up(50)
    output(scores)
