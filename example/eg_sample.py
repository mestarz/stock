import numpy

import data
import utils

if __name__ == '__main__':
    sdata = data.DataMacine().sample_only_price_volatility(utils.CoreSymbol.沪深300ETF_510300.value,
                                                           utils.Frequency.Frequency_Day, 2023)
    print(sdata)

    N = data.Normalize(100, sdata)
    print(N.normalize_list(sdata))
