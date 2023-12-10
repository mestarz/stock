import random

import numpy
import numpy as np
import datetime

import utils


class DataMacine:
    def __init__(self, sample_num: int = 30):
        self.sample_num = sample_num
        # 使用时间戳作为随机种子
        random_seed = int(datetime.datetime.now().timestamp())
        self.random = random.Random(random_seed)

    def sample(self, symbol: str, frequency: utils.Frequency, year: int) -> [np.array]:
        if not utils.is_valid_symbol(symbol):
            assert False, "invalid symbol: " + symbol

        end = datetime.datetime(year, 12, 31, 23, 59, 59)
        expand_num = self.sample_num * 5
        data = utils.get_data_n(symbol, frequency, expand_num, end)
        if data is None:
            assert False, "get data failed: " + symbol

        index = self.random.randint(0, expand_num - self.sample_num)
        # 收盘价
        close = data['close'].values.tolist()
        close = close[index:index + self.sample_num]
        # 容量
        volume = data['volume'].values.tolist()
        volume = volume[index:index + self.sample_num]
        result = [[close[i], volume[i]] for i in range(len(close))]
        return result

    def sample_normalize(self, symbol: str, frequency: utils.Frequency, year: int) -> [np.array]:
        data = self.sample(symbol, frequency, year)
        close = [data[i][0] for i in range(len(data))]
        volume = [data[i][1] for i in range(len(data))]
        # 收盘价标准化
        close = self.normalize_close(close)
        # 容量标准话化
        volume = self.normalize_volume(volume)
        result = [[close[i], volume[i]] for i in range(len(close))]
        return np.array(result)

    def sample_only_price(self, symbol: str, frequency: utils.Frequency, year: int) -> [np.array]:
        data = self.sample(symbol, frequency, year)
        close = [data[i][0] for i in range(len(data))]
        # 收盘价标准化
        close = self.normalize_close(close)
        result = [[close[i]] for i in range(len(close))]
        return np.array(result)

    def sample_normalize_n(self, symbol: str, frequency: utils.Frequency, year: int, n: int) -> [np.array]:
        sample_num_back = self.sample_num
        if n > 10:
            self.sample_num = self.sample_num * 10
        else:
            self.sample_num = self.sample_num * n

        data = self.sample(symbol, frequency, year)
        self.sample_num = sample_num_back

        result = []
        for i in range(n):
            index = random.randint(0, len(data) - self.sample_num)
            result.append(data[index:index + self.sample_num])
        return np.array(result)

    def normalize_close(self, close_list: [float]) -> [float]:
        # get up% and down%
        normalize1 = [close_list[i] - close_list[i - 1] for i in range(1, len(close_list))]
        normalize1 = [0] + normalize1
        normalize1 = [normalize1[i] - min(normalize1) for i in range(len(normalize1))]
        # 取六位小数
        normalize1 = [round(normalize1[i], 6) for i in range(len(normalize1))]
        return normalize1

    def normalize_volume(self, volume_list: [float]) -> [float]:
        # 缩放倍数
        num = max(volume_list) / 1000
        normalize1 = [volume_list[i] / num for i in range(len(volume_list))]
        # 取六位小数
        normalize1 = [round(normalize1[i], 6) for i in range(len(normalize1))]
        return normalize1
