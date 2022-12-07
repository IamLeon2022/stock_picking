# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 10:04:32 2021

@author: Leon
"""
import tushare as ts
import pandas as pd
import os
import numpy as np
import time
#from tqdm import tqdm


'''
获取股票历史数据
'''
mytoken = 'e8e2b35e23615af884fb92c30ee7a269b6f2b324459f1fd2c155cd82'
ts.set_token(mytoken)
ts.set_token(mytoken)
save_path = 'stock'
#给定保存路径
pro = ts.pro_api()

def getNoramlData():
    #获取基础信息数据，包括股票代码、名称、地域，行业，全称，上市日期，市场类型，交易所代码，沪深港通标
    pool = pro.stock_basic(exchange='',
                           list_status='L',
                           adj='qfq',
                           fields='ts_code,symbol,name,area,industry,fullname,list_date, market,exchange,is_hs')
    
    #从中筛选出主板和中小版存入stock中（只考虑此板块）
    pool = pool[pool['market'].isin(['主板', '中小板'])].reset_index()
    pool.to_csv(os.path.join(save_path, 'company_info.csv'), index=False, encoding='ANSI')
    
    print('获得上市股票总数：', len(pool)-1)
    j = 1
    #循环获取如上各家股票信息，通用行情接口。（2018到2021年的所有数据）
    for i in pool.ts_code:
        print('正在获取第%d家，股票代码%s.' % (j, i))
        #接口限制访问200次/分钟，加一点微小的延时防止被ban
        path = os.path.join(save_path, 'OldData', i + '_NormalData.csv')
        j += 1

        time.sleep(0.301)
        #各类长短期均线数据，以及换手率，量比。
        df = ts.pro_bar(ts_code=i, adj='qfq', start_date=startdate, end_date=enddate,
                        ma=[5, 10, 13, 21, 30, 60, 120], factors=['tor', 'vr'])
        try:
            df = df.sort_values('trade_date', ascending=True)
            df.to_csv(path, index=False,encoding='ANSI')
        except:
            print(i)
    
    #return pool
    


#每日涨停价格统计
def getLimitData():
    #获取基础信息数据，包括股票代码、名称、地域，行业，全称，上市日期，市场类型，交易所代码，沪深港通标
    pool = pro.stock_basic(exchange='',
                           list_status='L',
                           adj='qfq',
                           fields='ts_code,symbol,name,area,industry,fullname,list_date, market,exchange,is_hs')
    #print(pool.head())

    # 主板和中心板
    pool = pool[pool['market'].isin(['主板', '中小板'])].reset_index()
    

    print('获得上市股票总数：', len(pool)-1)
    j = 300
    for i in pool.ts_code[300:]:
        print('正在获取第%d家，股票代码%s.' % (j, i))
        #接口限制访问200次/分钟，加一点微小的延时防止被ban
        path = os.path.join(save_path, 'LimitData', i + '.csv')
        j += 1
        # if os.path.exists(path):
        #     continue
        time.sleep(1.01)
        #得到包括交易日期，ts代码，昨日收盘价，涨停价，跌停价
        df = pro.stk_limit(ts_code=i,
                           adj='qfq',
                       start_date=startdate,
                       end_date=enddate)
        df = df.sort_values('trade_date', ascending=True)
        df.to_csv(path, index=False,encoding='ANSI')    


        
 #获取指数日线行情       
def getIndexData():
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
        #分别获取交易日，开盘收盘最低最高点位，昨日收盘点，，涨跌点，涨跌幅，成交量，成交额
        df = pro.index_daily(ts_code=i,
                             start_date=startdate,
                             end_date=enddate,
                             fields='ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, '
                                    'vol, amount')
        df = df.sort_values('trade_date', ascending=True)
        df.to_csv(path, index=False)
        
        
        
def getOtherData():
    index_df = pd.read_csv(os.path.join(save_path, 'OldData', '000001.SH' + '_NormalData.csv'))

    day = np.sort(list(index_df['trade_date']))


    # 获取沪深港通资金流向
    df_all = pd.DataFrame()
    skip = 200
    for i in range(0, len(day), skip):  # 每次最多返回300条
        sd = str(day[i])
        if i + skip-1 > len(day):
            ed = str(day[-1])
        else:
            ed = str(day[i+skip-1])
        df = pro.moneyflow_hsgt(start_date=sd, end_date=ed)
        time.sleep(0.5)
        df_all = pd.concat((df_all, df))
    path = os.path.join(save_path, 'OhterData', 'moneyflow_hsgt' + '.csv')
    df_all.to_csv(path, index=False)





if __name__ == '__main__':
    #设置起始日期
    startdate = '20180101'
    enddate = '20211031'
    #主程序
    getNoramlData()
    #a=getNoramlData()
    getIndexData()
    getLimitData()
    getOtherData()#（涨跌停数据无法调取，只调取了资金流向数据，两千积分我怎么能调得到）
    #getMoneyData()#（个股资金流向数据无法调取）


