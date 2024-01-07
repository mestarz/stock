import os

from src.internal.driver.bond import analyse_divergence_score_bond, get_topn_bond


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
    top = get_topn_bond(30)
    output([x[0] for x in top])
