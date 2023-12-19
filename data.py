import random

import numpy
import numpy as np
import datetime
from scipy.stats import norm
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
            assert False, "get database failed: " + symbol

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
        result = [[close[i]] for i in range(len(close))]
        return np.array(result)

    def sample_only_price_volatility(self, symbol: str, frequency: utils.Frequency, year: int) -> [np.array]:
        data = self.sample_only_price(symbol, frequency, year)
        volatility = [(data[i] - data[i - 1]) / data[i - 1] for i in range(1, len(data))]
        volatility = np.array(volatility).flatten()
        volatility = [0] + volatility
        volatility = [volatility[i] * 100 for i in range(len(volatility))]
        return volatility

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


class Normalize:
    def __init__(self, field: int, data: [float]):
        # 保留元数据
        self.src_data = data
        # 计算绝对值
        self.abs_data = [abs(data[i]) for i in range(len(data))]
        # 计算标准差
        self.std = np.std(self.abs_data)
        # 计算平均值
        self.mean = np.mean(self.abs_data)

        num_step = 100 * field
        # 创建一组 x 值
        x = np.linspace(0, 10, num_step)
        # 计算正态分布的概率密度函数
        pdf_values = norm.pdf(x, self.mean, self.std)
        # 计算累计概率密度函数
        step = (10 - 0) / num_step
        li = [0]
        for i in range(1, len(pdf_values)):
            li.append(li[i - 1] + step * pdf_values[i - 1])
        li.append(1)

        # 划分区间
        field_step = 1 / (field / 2)
        self.slice = []
        start = 0
        for i in range(len(li)):
            if li[i] >= start:
                self.slice.append(i / num_step)
                start += field_step

        self.slice = [-x for x in reversed(self.slice)][:-1] + self.slice
        self.slice = np.array(self.slice) * 10

    def normalize(self, data: float) -> int:
        for i in range(len(self.slice)):
            if i == len(self.slice) - 1:
                return i
            if self.slice[i] <= data < self.slice[i + 1]:
                return i
        return len(self.slice) - 1

    def normalize_list(self, data: [float]) -> [int]:
        return [self.normalize(data[i]) for i in range(len(data))]
