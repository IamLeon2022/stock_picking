import tushare as ts
import pandas as pd
import os
import time

"""
获取历史数据
"""

mytoken = 'e8e2b35e23615af884fb92c30ee7a269b6f2b324459f1fd2c155cd82'
ts.set_token(mytoken)
ts.set_token(mytoken)
save_path = 'stock/stock'
pro = ts.pro_api()


def RefreshNoramlData():
    #获取基础信息数据，包括股票代码、名称、上市日期、退市日期等
    pool = pro.stock_basic(exchange='',
                           list_status='L',
                           adj='qfq',
                           fields='ts_code,symbol,name,area,industry,fullname,list_date, market,exchange,is_hs')
    #print(pool.head())

    # 这里只考虑主板和中小板
    pool = pool[pool['market'].isin(['主板', '中小板'])].reset_index()
    pool.to_csv(os.path.join(save_path, 'company_info.csv'), index=False, encoding='ANSI')

    # print('获得上市股票总数：', len(pool)-1)
    k = 1
    for i in pool.ts_code:
        print('正在获取第%d家，股票代码%s.' % (k, i))
        path = os.path.join(save_path, 'OldData', i + '_NormalData.csv')
        k += 1
        df = ts.pro_bar(ts_code=i, adj='qfq', start_date=startdate, end_date=enddate,
                        ma=[5, 10, 13, 21, 30, 60, 120], factors=['tor', 'vr'])
        df = df.sort_values('trade_date', ascending=True)
        df = df.reset_index(drop=True)

        if len(df) == 0:
            continue
        #判断是否已经存在该股票数据
        if not os.path.exists(path):
            df.to_csv(path, index=False)
        else:
            f = open(path, 'a+', encoding='utf-8')
            col = list(df.columns)
            for j in range(len(df)):
                write_info = ''
                for j2 in range(len(col)):
                    write_info = write_info + str(df[col[j2]][j])
                    if j2 != len(col) - 1:
                        write_info = write_info + ','
                f.write(write_info + '\n')
            f.close()


def RefreshIndexData():
    # 上交所指数信息
    df = pro.index_basic(market='SSE')
    df.to_csv(os.path.join(save_path, 'SSE.csv'), index=False, encoding='ANSI')

    # 深交所指数信息
    df = pro.index_basic(market='SZSE')
    df.to_csv(os.path.join(save_path, 'SZSE.csv'), index=False, encoding='ANSI')

    # 获取指数历史信息
    # 这里获取几个重要的指数 【上证综指，上证50，上证A指，深证成指，深证300，中小300，创业300，中小板综，创业板综】
    index = ['000001.SH', '000016.SH', '000002.SH', '399001.SZ', '399007.SZ', '399008.SZ', '399012.SZ', '399101.SZ',
             '399102.SZ']
    for i in index:
        path = os.path.join(save_path, 'OldData', i + '_NormalData.csv')
        df = pro.index_daily(ts_code=i,
                             start_date=startdate,
                             end_date=enddate,
                             )
        df = df.sort_values('trade_date', ascending=True)
        df = df.reset_index(drop=True)


        if len(df) == 0:
            continue
        if not os.path.exists(path):
            df.to_csv(path, index=False)
        else:
            f = open(path, 'a+', encoding='utf-8')
            col = list(df.columns)
            for j in range(len(df)):
                write_info = ''
                for j2 in range(len(col)):
                    write_info = write_info + str(df[col[j2]][j])
                    if j2 != len(col) - 1:
                        write_info = write_info + ','
                f.write(write_info + '\n')
            f.close()


if __name__ == '__main__':
    #设置起始日期
    startdate = '20211101'
    enddate = '20211219'
    #主程序
    #RefreshNoramlData()
    RefreshIndexData()
