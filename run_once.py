import pandas as pd

from utils import is_valid_symbol


def valid_symbol(i: int) -> [str]:
    li = []
    sym1 = "SHSE." + str(i).zfill(6)
    sym2 = "SZSE." + str(i).zfill(6)
    if is_valid_symbol(sym1):
        li.append(sym1)
    if is_valid_symbol(sym2):
        li.append(sym2)
    return li


def test_update_symbols():
    valid_list = []

    # 沪市A股, 创业板, 科创版
    i = 0
    max_symbol_num = 999
    while i < max_symbol_num:
        for front in [600, 601, 603, 605, 300, 688]:
            num = front * 1000 + i
            valid_list = valid_list + valid_symbol(num)
        i = i + 1

        if len(valid_list) > 100:
            csv = pd.DataFrame({"name": valid_list})
            csv.to_csv('./data/symbol.data', mode='a', header=False, index=False)
            valid_list = []

    csv = pd.DataFrame({"name": valid_list})
    csv.to_csv('./data/symbol.data', mode='a', header=False, index=False)


test_update_symbols()
