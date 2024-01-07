import os

from src.internal.data.configure import root_path
from src.internal.database.database import get_all_stocks, get_n_fundamental_before_now, get_n_price_before_now, \
    Frequency
from src.internal.driver.stock import get_topn_score_up, get_weight_by_volatility, set_fundamental
from src.internal.score import score, chaos_operations


# 获取全部股票,根据divergence_score_up和divergence_score_down计算得分，将得分写入到data/score.data文件中
# data/score.data文件中的数据格式为：股票代码,做多得分,做空得分,波动率得分
def analyse_divergence_score():
    # 读取股票代码
    symbol_list = get_all_stocks()['all']

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
    score_manager.add_score_pass(chaos_operations.StockFluctuateLimit())
    score_manager.add_score_pass(chaos_operations.FundamentalLimit())

    # 遍历所有股票代码，计算得分
    with open(os.path.join(root_path, 'data/score.data'), 'w') as f:
        for symbol in symbol_list:
            if len(symbol) == 0:
                continue
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


# 将股票代码及占比导出到文件中
# 同花顺可用
def output(datas: [[]], filename: str):
    # 计算波动率
    weight_dict = get_weight_by_volatility(datas)
    # 将[股票代码,占比]写入文件中
    with open(os.path.join(root_path, 'data/' + filename), 'w') as f:
        for key in weight_dict.keys():
            f.write(key + ',' + str(weight_dict[key]) + '\n')
    # 同时将data/output_stock.txt拷贝到桌面
    os.system('cp ' + os.path.join(root_path, 'data/' + filename) + ' ~/Desktop')


# 将股票代码导出到文件中
# 东方财富可用
def output_dfcf(data: [[]], filename: str):
    # 将股票代码写入文件中
    with open(os.path.join(root_path, 'data/' + filename), 'w') as f:
        for x in data:
            symbol = x[0]
            # 去掉前缀
            if symbol.startswith('SHSE'):
                symbol = symbol[5:]
            elif symbol.startswith('SZSE'):
                symbol = symbol[5:]
            else:
                assert False and "symbol error"
            f.write(symbol + '\n')

    # 同时将data/stock.txt拷贝到桌面
    os.system('cp ' + os.path.join(root_path, 'data/' + filename) + ' ~/Desktop')


if __name__ == '__main__':
    analyse_divergence_score()
    scores = get_topn_score_up(50)
    output(scores, 'output_stock.txt')
    scores = get_topn_score_up(20)
    output_dfcf(scores, 'stock.txt')
