import pandas as pd
from gm.api import get_instruments, set_token, current
from gm.enum import SEC_TYPE_BOND_CONVERTIBLE
import src.internal.data.configure as configure

# 设置token， 查看已有token ID,在用户-密钥管理里获取
set_token(configure.token)


# 获取所有可转债的基本信息
# 过滤掉已退市、一年内到期的可转债
# 过滤掉刚上市一年内的可转债
def get_all_bond_info() -> pd.DataFrame:
    df = get_instruments(symbols=None, exchanges=None, sec_types=SEC_TYPE_BOND_CONVERTIBLE, df=True,
                         fields=['symbol', 'listed_date', 'delisted_date', 'conversion_price', 'underlying_symbol'])

    # 过滤掉最近一年内上市的可转债
    up_time_3_month_ago = pd.Timestamp.today() - pd.Timedelta(days=365)
    df = df[df['listed_date'] < up_time_3_month_ago.strftime('%Y-%m-%d')]

    # 过滤掉最近一年到期或者已经过期的可转债
    end_time_3_month_ago = pd.Timestamp.today() + pd.Timedelta(days=365)
    df = df[df['delisted_date'] > end_time_3_month_ago.strftime('%Y-%m-%d')]

    # 获取债券价格
    bond_symbols = df['symbol'].values.tolist()
    bond_prices = pd.DataFrame(current(symbols=bond_symbols, fields='symbol, price'))

    # 获取正股价格
    underlying_symbols = df['underlying_symbol'].values.tolist()
    underlying_prices = pd.DataFrame(current(symbols=underlying_symbols, fields='symbol, price'))

    # 计算转股溢价
    # 转股价值 = (100 / 转股价格) * 正股价格
    # 转股溢价 = (债券价值 - 转股价值) / 转股价值
    def get_conversion_premium(index: int):
        # 获取正股代码
        underlying_symbol = underlying_symbols[index]
        # 在正股价格中找到对应的正股价格
        underlying_price = underlying_prices[underlying_prices['symbol'] == underlying_symbol]['price'].values[0]
        # 获取转股价格
        conversion_price = df['conversion_price'].values[index]
        # 获取债券代码
        bond_symbol = bond_symbols[index]
        # 获取债券价格
        bond_price = bond_prices[bond_prices['symbol'] == bond_symbol]['price']
        if len(bond_price.values) == 0:
            return pd.NA
        bond_price = bond_price.values[0]
        # 转股价值
        conversion_value = (100 / conversion_price) * underlying_price
        # 转股溢价
        conversion_premium = (bond_price - conversion_value) / conversion_value
        return conversion_premium

    conversion_premium_list = [get_conversion_premium(i) for i in range(len(df))]
    df['conversion_premium'] = conversion_premium_list
    df = df.dropna()
    return df


if __name__ == '__main__':
    infos = get_all_bond_info()
    print(infos)
