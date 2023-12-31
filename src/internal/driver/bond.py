import os
from src.internal.database.database import get_n_price_before_now, Frequency
from src.internal.database.bond import get_all_bond_info
import src.internal.score.score as score
import src.internal.score.chaos_operations as chaos_operations
import src.internal.score.cb_four_factors as cb_four_factors


# 获取全部可转债,根据divergence_score_up和divergence_score_down计算得分，将得分写入到data/score_bond.data文件中
# data/score_bond.data文件中的数据格式为：可转债代码,做多得分,做空得分,波动率
def analyse_divergence_score_bond():
    # 获取项目根目录
    root_path = os.path.dirname(os.path.dirname(__file__))

    # 读取可转债代码
    bond_info = get_all_bond_info()
    symbol_list = bond_info['symbol'].values.tolist()
    # 转股溢价
    conversion_premium_list = bond_info['conversion_premium'].values.tolist()

    # 构造得分系统
    # score
    score_manager = score.ScorePassManager()
    score_manager.add_score_pass(chaos_operations.AlligatorLine(2))
    score_manager.add_score_pass(chaos_operations.FirstInnerBuySellPoint(1))
    score_manager.add_score_pass(chaos_operations.SecondInnerBuySellPoint(2))
    score_manager.add_score_pass(chaos_operations.ThirdInnerBuySellPoint(4))
    score_manager.add_score_pass(cb_four_factors.CBFourFactors(2))
    # limit
    score_manager.add_score_pass(cb_four_factors.CBondLimit())

    # 遍历所有可转债代码，计算得分
    with open(os.path.join(root_path, 'data/score_bond.data'), 'w') as f:
        for i in range(len(symbol_list)):
            symbol = symbol_list[i]
            # 获取转股溢价
            conversion_premium = conversion_premium_list[i]
            # 获取近日的数据
            df = get_n_price_before_now(symbol, Frequency.Frequency_H, 60)
            df['conversion_premium'] = [conversion_premium] * len(df)
            # 计算做多得分
            score_up = score_manager.run_up(df)
            # 计算做空得分
            score_down = score_manager.run_down(df)
            # 计算波动率得分
            score_volatility = df['volatility'].values[-1]
            # 将得分写入文件
            f.write(symbol + ',' + str(score_up) + ',' + str(score_down) + ',' + str(score_volatility) + '\n')


# 读取data/score_bond.data文件中的数据，根据做多得分和做空得分进行排序，选取前n个可转债，作为返回值
# 先按做多得分排序，做多得分越高，排名越靠前，如果做多得分相同，按做空得分排序，做空得分越高，排名越靠后
def get_topn_bond(n: int = 100) -> [[]]:
    # 获取项目根目录
    root_path = os.path.dirname(os.path.dirname(__file__))

    # 读取可转债代码
    with open(os.path.join(root_path, 'data/score_bond.data'), 'r') as f:
        score_list = f.read().splitlines()

    score_list = [x.split(',') for x in score_list]

    # 过滤掉做多得分为-inf的可转债
    score_list = [x for x in score_list if x[1] != '-inf']

    # 根据做多得分-做空得分进行排序
    score_list.sort(key=lambda x: float(x[1]) - float(x[2]), reverse=True)

    # 选取前100个可转债
    score_list = score_list[:n]

    return score_list


# 将可转债代码导出到文件data/output_bond.data中
def output(symbols: [str]):
    # 获取项目根目录
    root_path = os.path.dirname(os.path.dirname(__file__))

    with open(os.path.join(root_path, 'data/output_bond.txt'), 'w') as f:
        for symbol in symbols:
            f.write(symbol + '\n')
    # 同时将data/output_bond.txt拷贝到桌面
    os.system('cp ' + os.path.join(root_path, 'data/output_bond.txt') + ' ~/Desktop')


if __name__ == '__main__':
    analyse_divergence_score_bond()
    top = get_topn_bond(50)
    output([x[0] for x in top])
