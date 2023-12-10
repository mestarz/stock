import datetime

from utils import Frequency
from utils import CoreSymbol
import utils

data = utils.get_random_symbol(100)
tmp: str = data[0]
d = utils.get_data_n(CoreSymbol.沪深300ETF_510300.value, Frequency.Frequency_Day, 20, utils.now)

print(d.columns.tolist())
print(d[['volume', 'close']])

high = d['high'].values.tolist()
low = d['low'].values.tolist()
open = d['open'].values.tolist()
close = d['close'].values.tolist()
y1 = [(high[i] - low[i]) / low[i] for i in range(len(high))]
y2 = [abs(open[i] - close[i]) / min(open[i], close[i]) for i in range(len(high))]
y3 = [(y1[i] + y2[i]) / 2 for i in range(len(y1))]

x = range(len(high))

import matplotlib.pyplot as plt
import numpy as np


def normalize(li: [float]):
    normalized_list = (np.array(li) - min(li)) / (max(li) - min(li))
    return normalized_list


plt.plot(x, normalize(y1), label='high-low', color='blue')
plt.plot(x, normalize(y2), label='open-close', color='red')
plt.plot(x, normalize(y3), label='y3', color='black')

plt.show()
