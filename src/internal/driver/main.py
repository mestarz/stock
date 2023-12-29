import os

from gm.api import get_history_constituents

from src.internal.database.database import get_n_price_before_now, Frequency, get_all_stocks
from src.internal.score.divergence import divergence_score_up, divergence_score_down


# 获取全部股票,根据divergence_score_up和divergence_score_down计算得分，将得分写入到data/score.data文件中
# data/score.data文件中的数据格式为：股票代码,做多得分,做空得分,波动率得分
def analyse_divergence_score():
    # 获取项目根目录
    root_path = os.path.dirname(os.path.dirname(__file__))

    # 读取股票代码
    symbol_list = get_all_stocks()['all']

    # 遍历所有股票代码，计算得分
    with open(os.path.join(root_path, 'data/score.data'), 'w') as f:
        for symbol in symbol_list:
            # 获取最近300日的数据
            df = get_n_price_before_now(symbol, Frequency.Frequency_H, 300)
            # 计算做多得分
            score_up = divergence_score_up(df)
            # 计算做空得分
            score_down = divergence_score_down(df)
            # 计算波动率得分
            score_volatility = df['volatility'].values[-1]
            # 将得分写入文件
            f.write(symbol + ',' + str(score_up) + ',' + str(score_down) + ',' + str(score_volatility) + '\n')


# 读取data/score.data文件中的数据，根据做多得分进行排序，选取前100个股票，作为返回值
def get_top_100_score_up():
    # 获取项目根目录
    root_path = os.path.dirname(os.path.dirname(__file__))

    # 读取股票代码
    with open(os.path.join(root_path, 'data/score.data'), 'r') as f:
        score_list = f.read().splitlines()

    # 根据做多得分进行排序
    score_list.sort(key=lambda x: float(x.split(',')[1]), reverse=True)

    # 选取前100个股票
    score_list = score_list[:100]
    score_list = [x.split(',') for x in score_list]
    return score_list


# 根据波动率计算每个股票占比，波动率越高占比越低，总占比为1
# 输出是股票代码和占比的字典
# 输入是列表[[股票代码,做多得分,做空得分,波动率得分],...]
def get_weight_by_volatility(data: []):
    # 计算每个股票的波动率的倒数
    reciprocals = [1 / float(x[3]) for x in data]

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


if __name__ == '__main__':
    # analyse_divergence_score()
    scores = get_top_100_score_up()
    print(get_weight_by_volatility(scores))
