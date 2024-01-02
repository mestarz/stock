# 读取src/internal/data/output_bond.txt中的可转债数据，计算存在风险的可转债，并将结果写入data/risk_bond.data文件中，同时将data/risk_bond.data拷贝到桌面
import os

from src.internal.database.database import get_n_price_before_now, Frequency
from src.internal.score import score, chaos_operations, cb_four_factors


# 读取文件中的可转债数据，将名字作为列表返回
def read_output_bond() -> [str]:
    # 获取项目根目录
    root_path = os.path.dirname(os.path.dirname(__file__))

    with open(os.path.join(root_path, 'data/output_bond.txt'), 'r') as f:
        symbols = f.read().splitlines()

    return symbols


if __name__ == '__main__':
    symbols = read_output_bond()
    root_path = os.path.dirname(os.path.dirname(__file__))

    # 构造风险系统
    risk_manager = score.ScorePassManager()
    risk_manager.add_score_pass(chaos_operations.ChaosLimit())
    risk_manager.add_score_pass(cb_four_factors.CBondLimit())

    # 遍历可转债代码，判断所有计算出来做多得分为-inf的可转债，将其写入data/risk_bond.data文件中
    with open(os.path.join(root_path, 'data/risk_bond.data'), 'w') as f:
        for symbol in symbols:
            # 获取最近300日的数据
            df = get_n_price_before_now(symbol, Frequency.Frequency_H, 60)
            # 计算做多得分
            score_up = risk_manager.run_up(df)
            # 如果做多得分为-inf，则将可转债代码写入文件中
            if score_up == -float('inf'):
                f.write(symbol + '\n')

    # 将data/risk_bond.data拷贝到桌面
    os.system('cp ' + os.path.join(root_path, 'data/risk_bond.data') + ' ~/Desktop')
