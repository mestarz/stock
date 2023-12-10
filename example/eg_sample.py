import numpy

import data
import utils

if __name__ == '__main__':
    data = data.DataMacine().sample_normalize_n("SHSE.600000", utils.Frequency.Frequency_Day, 2020, 100)
    print(data)
    print(data.shape)
