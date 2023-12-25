import os

from src.database.database import get_n_price_before_now, Frequency
from src.score.divergence import divergence_score_up, divergence_score_down


# 遍历 data/symbol.data文件中的所有股票代码，根据divergence_score_up和divergence_score_down计算得分，将得分写入到data/score.data文件中
# data/score.data文件中的数据格式为：股票代码,做多得分,做空得分
def analyse_divergence_score():
    # 获取项目根目录
    root_path = os.path.dirname(os.path.dirname(__file__))

    # 读取股票代码
    with open(os.path.join(root_path, 'data/symbol.data'), 'r') as f:
        symbol_list = f.read().splitlines()

    # 遍历所有股票代码，计算得分
    with open(os.path.join(root_path, 'data/score.data'), 'w') as f:
        for symbol in symbol_list:
            # 获取最近300日的数据
            df = get_n_price_before_now(symbol, Frequency.Frequency_H, 300)
            # 计算做多得分
            score_up = divergence_score_up(df)
            # 计算做空得分
            score_down = divergence_score_down(df)
            # 将得分写入文件
            f.write(symbol + ',' + str(score_up) + ',' + str(score_down) + '\n')


# 读取data/score.data文件中的数据，根据做多得分进行排序，选取前50个股票代码，作为返回值
# 返回值为一个列表，列表中的元素为股票代码
def get_top_50_score_up():
    # 获取项目根目录
    root_path = os.path.dirname(os.path.dirname(__file__))

    # 读取股票代码
    with open(os.path.join(root_path, 'data/score.data'), 'r') as f:
        score_list = f.read().splitlines()

    # 根据做多得分进行排序
    score_list.sort(key=lambda x: float(x.split(',')[1]), reverse=True)

    # 选取前50个股票代码
    top_50_score_up = []
    for i in range(50):
        top_50_score_up.append(score_list[i].split(',')[0])

    return top_50_score_up


if __name__ == '__main__':
    scores = get_top_50_score_up()
    print(scores)
