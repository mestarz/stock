from __future__ import annotations
from collections import OrderedDict


class Stock:
    def __init__(self, symbol: str):
        self.symbol = symbol

    def __eq__(self, other: Stock):
        return self.symbol == other.symbol

    def __hash__(self):
        return hash(self.symbol)

    def data(self):
        return self.symbol

    def display(self):
        print(self.symbol)


class StockPool:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.pool = OrderedDict()
        self.set = set()

    def append(self, elem: Stock) -> [None | Stock]:
        if elem in self.set:
            del self.pool[elem]
            self.pool[elem] = None
            return None
        item = None
        if len(self.pool.keys()) >= self.capacity:
            item = self.pool.popitem(last=False)[0]
            self.set.remove(item)
        self.pool[elem] = None
        self.set.add(elem)
        return item

    def append_list(self, elms: list) -> [None | list]:
        items = []
        for elem in elms:
            item = self.append(elem)
            if item is not None:
                items.append(item)
        return items

    def empty(self) -> bool:
        return bool(self.pool)

    def data(self):
        return [e.data() for e in self.pool.keys()]

    def display(self) -> None:
        names = [e.data() for e in self.pool.keys()]
        print(names)


if __name__ == '__main__':
    pool = StockPool(2)
    pool.append(Stock("1"))
    pool.append(Stock("3"))
    a = pool.append(Stock("2"))
    a.display()
    pool.display()
    pool.append_list([Stock("3"), Stock("1")])
    pool.display()
