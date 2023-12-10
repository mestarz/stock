from StockPool import Stock, StockPool
from deepdiff import DeepDiff
import unittest


class TestStockPool(unittest.TestCase):
    def assert_list(self, result, target):
        diff = DeepDiff(result, target)
        if 0 != len(diff):
            print(result)
            print(target)
            print(diff)
        self.assertEqual(len(diff), 0)

    def test_append_elem(self):
        pool = StockPool(3)
        pool.append(Stock("1"))
        pool.append(Stock("2"))
        data = pool.data()
        self.assert_list(data, ["1", "2"])

        pool.append(Stock("1"))
        data = pool.data()
        self.assert_list(data, ["2", "1"])

        pool.append(Stock("3"))
        data = pool.data()
        self.assert_list(data, ["2", "1", "3"])

        pool.append(Stock("4"))
        data = pool.data()
        self.assert_list(data, ["1", "3", "4"])

    def test_appends_list(self):
        pool = StockPool(4)
        pool.append_list([Stock("1"), Stock("2"), Stock("2"), Stock("4")])
        data = pool.data()
        self.assert_list(data, ["1", "2", "4"])

        pool.append_list([Stock("1"), Stock("8"), Stock("9")])
        data = pool.data()
        self.assert_list(data, ["4", "1", "8", "9"])
