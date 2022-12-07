# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 21:06:00 2021

@author: Leon
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 20:47:12 2021

@author: Leon
"""

import pandas as pd
import copy
import os

base_path = 'stock(shiyan)\\stock'

class ChipDistribution():

    def __init__(self):
        self.Chip = {} # 当前获利盘
        self.ChipList = {}  # 所有的获利盘的

    def get_data(self):
        self.data = pd.read_csv(os.path.join(base_path,'OldData','000001.SZ_NormalData.csv'),encoding = 'ANSI')
        #self.data = pd.read_excel(os.path.join('000001.SZ.xlsx'))
        
    def calcuJUN(self,dateT,highT, lowT, volT, TurnoverRateT, A, minD):

        x =[]
        l = (highT - lowT) / minD
        for i in range(int(l)):
            x.append(round(lowT + i * minD, 2))
        length = len(x)
        eachV = volT/length
        for i in self.Chip:
            self.Chip[i] = self.Chip[i] *(1 -TurnoverRateT * A)
        for i in x:
            if i in self.Chip:
                self.Chip[i] += eachV *(TurnoverRateT * A)
            else:
                self.Chip[i] = eachV *(TurnoverRateT * A)
        import copy
        self.ChipList[dateT] = copy.deepcopy(self.Chip)



    def calcuSin(self,dateT,highT, lowT,avgT, volT,TurnoverRateT,minD,A):
        x =[]
        l = (highT - lowT) / minD
        for i in range(int(l)):
            x.append(round(lowT + i * minD, 2))

        #length = len(x)

        #计算仅仅今日的筹码分布
        tmpChip = {}
        #eachV = volT/length


        #极限法分割去逼近
        for i in x:
            x1 = i
            x2 = i + minD
            h = 2 / (highT - lowT)
            s= 0
            if i < avgT:
                y1 = h /(avgT - lowT) * (x1 - lowT)
                y2 = h /(avgT - lowT) * (x2 - lowT)
                s = minD *(y1 + y2) /2
                s = s * volT
            else:
                y1 = h /(highT - avgT) *(highT - x1)
                y2 = h /(highT - avgT) *(highT - x2)

                s = minD *(y1 + y2) /2
                s = s * volT
            tmpChip[i] = s

        #筹码移出
        for i in self.Chip:
            self.Chip[i] = self.Chip[i] *(1 -TurnoverRateT * A)
        #筹码移入
        for i in tmpChip:
            if i in self.Chip:
                self.Chip[i] += tmpChip[i] *TurnoverRateT * A
            else:
                self.Chip[i] = tmpChip[i] *TurnoverRateT * A
        import copy
        self.ChipList[dateT] = copy.deepcopy(self.Chip)


    def calcu(self,dateT,highT, lowT,avgT, volT, TurnoverRateT,minD = 0.01, flag=1 , AC=1):
        if flag ==1:
            self.calcuSin(dateT,highT, lowT,avgT, volT, TurnoverRateT,A=AC, minD=minD)
        elif flag ==2:
            self.calcuJUN(dateT,highT, lowT, volT, TurnoverRateT, A=AC, minD=minD)

    def calcuChip(self, flag=1, AC=1):  #flag 使用哪个计算方式,    AC 衰减系数
        self.data['avg'] = (self.data['high'] + self.data['low'])/2
        low = self.data['low']
        high = self.data['high']
        vol = self.data['vol']
        TurnoverRate = self.data['turnover_rate']
        #TurnoverRate = self.data['TURNRATE']
        avg = self.data['avg']
        date = self.data['trade_date']

        for i in range(len(date)):
        #     if i < 90:
        #         continue

            highT = high[i]
            lowT = low[i]
            volT = vol[i]
            TurnoverRateT = TurnoverRate[i]
            avgT = avg[i]
            # print(date[i])
            dateT = date[i]
            self.calcu(dateT,highT, lowT,avgT, volT, TurnoverRateT/100, flag=flag, AC=AC)  # 东方财富的小数位要注意，兄弟萌。我不除100懵逼了

        # 计算winner
    def winner(self,p=None):
            Profit = []
            date = self.data['trade_date']

            if p == None:  # 不输入默认close
                q = self.data['close']
                count = 0
                for i in self.ChipList:
                    # 计算目前的比例

                    chip = self.ChipList[i]
                    total = 0.0
                    be = 0
                    for i in chip:
                        total += float(i)#价格累加吗
                    #total += chip[i]
                    #不应该是筹码累加吗
                        if i < q[count]:
                            be += i
                        #be += chip[i]
                    if total != 0:
                        bili = be / total
                    else:
                        bili = 0
                    count += 1
                    Profit.append(bili)
            else:
                q = self.data[p]
                count = 0
                for i in self.ChipList:
                    # 计算目前的比例

                    Chip = self.ChipList[i]
                    total = 0.0
                    be = 0
                    for i in Chip:
                        total += float(i)#价格累加吗
                        if i < q[count]:
                            be += i
                        #be += chip[i]
                    if total != 0:
                        bili = be / total
                    else:
                        bili = 0
                    Profit.append(bili)

            #import matplotlib.pyplot as plt
            #plt.plot(date[len(date) - 200:-1], Profit[len(date) - 200:-1])
            #plt.show()

            return Profit

    def lwinner(self,N = 5, p=None):

        data = copy.deepcopy(self.data)
        date = data['date']
        ans = []
        for i in range(len(date)):
            print(date[i])
            if i < N:
                ans.append(None)
                continue
            self.data = data[i-N:i]
            self.data.index= range(0,N)
            self.__init__()
            self.calcuChip()    #使用默认计算方式
            a = self.winner(p)
            ans.append(a[-1])
        import matplotlib.pyplot as plt
        plt.plot(date[len(date) - 60:-1], ans[len(date) - 60:-1])
        plt.show()

        self.data = data
        return ans

import talib

if __name__ == "__main__":
    a=ChipDistribution()
    a.get_data() #获取数据
    a.calcuChip(flag=1, AC=1) #计算
    #print(a.winner()) #获利盘
    #a.cost(90) #成本分布

    a.data["winner"] = a.winner()

    #a.lwinner()
    
    
    #计算ZLCM    EMA
    a.data['zlcm'] = talib.EMA(a.data["winner"]*70,timeperiod=3)
    
    
    #计算SHCM   EMA
    a.data['close_1.1'] = a.data["close"]*1.1
    a.data['close_0.9'] = a.data["close"]*0.9
    a.data["winner_1.1"] = a.winner(p='close_1.1')
    a.data["winner_0.9"] = a.winner(p='close_0.9')
    a.data['SHCM'] = talib.EMA((a.data["winner_1.1"]-a.data['winner_0.9'])*80,timeperiod=3)
    a.data['zhuli']=(a.data['zlcm']/(a.data['SHCM']+a.data['zlcm']))*100
    a.data.to_csv(os.path.join(base_path,'OldData','000001.SZ_NormalData.csv'))

    



























