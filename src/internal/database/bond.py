import pandas as pd
import requests

# 请求头
EASTMONEY_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    # 'Referer': 'http://quote.eastmoney.com/center/gridlist.html',
}

# 债券基本信息表头
EASTMONEY_BOND_BASE_INFO_FIELDS = {
    'SECUCODE': 'symbol',
    'SECURITY_NAME_ABBR': 'name',
    'LISTING_DATE': 'start_date',
    'EXPIRE_DATE': 'end_date',
}


# 获取所有可转债的基本信息
# 过滤掉已退市、一年内到期的可转债
# 过滤掉刚上市一年内的可转债
def get_all_bond_info() -> pd.DataFrame:
    page = 1
    dfs: list[pd.DataFrame] = []
    columns = EASTMONEY_BOND_BASE_INFO_FIELDS
    while True:
        params = (
            ('sortColumns', 'PUBLIC_START_DATE'),
            ('sortTypes', '-1'),
            ('pageSize', '500'),
            ('pageNumber', f'{page}'),
            ('reportName', 'RPT_BOND_CB_LIST'),
            ('columns', 'ALL'),
            ('source', 'WEB'),
            ('client', 'WEB'),
        )

        url = 'http://datacenter-web.eastmoney.com/api/data/v1/get'
        json_response = requests.get(
            url, headers=EASTMONEY_REQUEST_HEADERS, params=params
        ).json()
        if json_response['result'] is None:
            break
        data = json_response['result']['data']
        df = pd.DataFrame(data).rename(columns=columns)[columns.values()]
        dfs.append(df)
        page += 1

    df = pd.concat(dfs, ignore_index=True)

    # 过滤掉未上市的数据
    df = df.dropna()
    # 过滤掉最近一年内上市的可转债
    up_time_3_month_ago = pd.Timestamp.today() - pd.Timedelta(days=365)
    df = df[df['start_date'] < up_time_3_month_ago.strftime('%Y-%m-%d')]

    # 过滤掉最近一年到期或者已经过期的可转债
    end_time_3_month_ago = pd.Timestamp.today() + pd.Timedelta(days=365)
    df = df[df['end_date'] > end_time_3_month_ago.strftime('%Y-%m-%d')]

    # 根据交易所替换股票代码
    # 以*.SH结尾的股票代码，替换为以SHSE为前缀的代码. eq. 600000.SH -> SHSE.600000
    # 以*.SZ结尾的股票代码，替换为以SZSE为前缀的代码. eq. 000001.SZ -> SZSE.000001
    df['symbol'] = df['symbol'].str.replace(r'(\d+)\.SH', r'SHSE.\1', regex=True)
    df['symbol'] = df['symbol'].str.replace(r'(\d+)\.SZ', r'SZSE.\1', regex=True)

    return df


if __name__ == '__main__':
    infos = get_all_bond_info()
    print(infos)
