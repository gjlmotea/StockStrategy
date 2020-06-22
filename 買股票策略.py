import csv
import os
import re
from decimal import *
getcontext().prec = 5

PriceWay =  []
csv_list = []
Date = []
Open = []
High = []
Low = []
Close = []
Profit = 0
Cost = 0

dataPath = "./data/"
for fileName in os.listdir(dataPath):
    if fileName[0:9] == 'STOCK_DAY':
        print(fileName)
        with open(dataPath+fileName, newline='') as csvfile:
            rows = csv.reader(csvfile)
            for row in rows:
                csv_list.append(row)
            csv_list.pop()

for i in range(2, len(csv_list)):
    match = re.search('[0-9]*/[0-9]*/[0-9]*',csv_list[i][0])
    if match:
        if csv_list[i][1] == '0':
            #成交股數為0 資料缺失
            continue
        Date.append(csv_list[i][0])
        Open.append(Decimal(str(float(csv_list[i][3]))))
        High.append(Decimal(str(float(csv_list[i][4]))))
        Low.append(Decimal(str(float(csv_list[i][5]))))
        Close.append(Decimal(str(float(csv_list[i][6]))))

#print(csv_list)

def MA(day:int) -> list:
    MA = []
    for i in range(day-1):
        MA.append(float(format(0, '.2f')))
    for i in range(day - 1, len(Close)):
        #print(i)
        Sum = 0
        for j in range(0, day):
            Sum += Close[i-j]
        #print(format(Sum/day, '.2f'))
        MA.append(float(format(Sum/day, '.2f')))
    return MA




'''印日期、開盤、最高、最低、收盤、MA1、MA2
print("Date    ", Date)
print("Open    ", Open)
print("High    ", High)
print("Low     ", Low)
print("Close   ", Close)
print("MA1:", n1, "days", MA1)
print("MA2:", n2, "days", MA2)
'''

buy_OB = False
sell_OB = False
displayMsg = False
Stocks = []

#########################################################################
""" 宇順專用 """
#Thold: Threshold
OpptThold = 1.6
RiskThold = 2.6
n1 = 3
n2 = 6
MA1 = MA(n1)
MA2 = MA(n2)
# n2 > n1
for i in range(len(Date)):
    #PriceWay.append(Decimal(str((Open[i] + Close[i] + Close[i]) / 3)))
    #PriceWay.append(Decimal(str((Close[i]) / 3 + 100)))
    PriceWay.append(Decimal(str(Close[i])))
print(PriceWay)
""" 宇順專用 """
#########################################################################



OpptThold = Decimal(str(OpptThold))
RiskThold = Decimal(str(RiskThold))

for i in range(n2+1, len(MA1)):
    if sell_OB or buy_OB:
        print("風險, 機會",float(Risk), float(Oppt))
    if sell_OB:
        if Open[i] < Close[i-1] and Close[i] < Close[i-1]:
            Oppt += 1
        elif Open[i] > Close[i-1] and Close[i] > Close[i-1]:
            Risk += 1
        else:
            Oppt += Decimal('0.6')
            Risk += Decimal('0.6')

    if buy_OB:
        if Open[i] > Close[i-1] and Close[i] > Close[i-1]:
            Oppt += 1
        elif Open[i] < Close[i-1] and Close[i] < Close[i-1]:
            Risk += 1
        else:
            Oppt += Decimal('0.6')
            Risk += Decimal('0.6')
    print()
    print()

    print(Date[i], MA1[i], MA2[i])

    if buy_OB:
        if buyInReady:
            if buyInPrice > Open[i]:
                print("**** 哥，你的單用更低的開盤價買到了！買入價格:", Open[i])
                Stocks.append(Decimal(Open[i]))
                buy_OB = False
            elif buyInPrice >= Low[i]:
                print("**** 哥，你成功買到單啦 **** 買入價格:", buyInPrice)
                Stocks.append(Decimal(buyInPrice))
                buy_OB = False
            else:
                print("**** 觀察價 低於 當日最低價，不執行買入 **** 價格:", buyInPrice, Low[i])
        if Risk > RiskThold:
            buy_OB = False
            print("======== BUY IN OB 信心不足 ========")
            print("風險, 機會",float(Risk), float(Oppt))
        if MA1[i] < MA2[i]:
            buy_OB = False
            print("======== 觀察信心不足 BUY IN OB MA1 低於 MA2 ========")
            print("風險, 機會",float(Risk), float(Oppt))
        if Oppt >= OpptThold and Risk < RiskThold:
            buyInReady = True
            print("!!!===== 明天掛單買入 =====!!!")

    if sell_OB:
        if sellOutReady:
            '''高5%才掛賣'''
            print("手上的股票有：", len(Stocks)," 張")
            for Stock in sorted(Stocks):
                print(Stock, end=',')
            print()

            if sellOutPrice < Open[i]:
                for Stock in reversed(Stocks):
                    if Open[i] > Stock * Decimal('1.05'):
                        print("**** 哥，你的單用開盤價賣出啦啊 **** 賣出價格:", Open[i])
                        print("************************* 此股之買入價格:", Stock)
                        print("************************* 哥，你的利潤是:", Decimal(Open[i]) - Decimal(Stock))
                        Profit += Decimal(Open[i]) - Decimal(Stock)
                        Cost += Stock
                        Stocks.remove(Stock)
                    else:
                        print("**** 賣價<1.05倍買價，成本負擔不起，不執行賣出", Stock)
                sell_OB = False
            elif sellOutPrice <= High[i]:
                for Stock in reversed(Stocks):
                    if sellOutPrice > Stock * Decimal('1.05'):
                        print("**** 哥，你的單賣出啦啊 **** 賣出價格:", sellOutPrice)
                        print("************************* 此股之買入價格:", Stock)
                        print("************************* 哥，你的利潤是:", Decimal(sellOutPrice) - Decimal(Stock))
                        Profit += Decimal(sellOutPrice) - Decimal(Stock)
                        Cost += Stock
                        Stocks.remove(Stock)
                    else:
                        print("**** 賣價<1.05倍買價，成本負擔不起，不執行賣出", Stock)
                sell_OB = False
            else:
                print("**** 沒人要用這個價格買:", sellOutPrice, High[i])
        if Risk > RiskThold or MA1[i] > MA2[i]:
            sell_OB = False
            print("======== 觀察信心不足 SELL OUT OB 信心不足 ========")
            print("風險, 機會",float(Risk), float(Oppt))
        if Oppt >= OpptThold and Risk < RiskThold:
            sellOutReady = True
            print("!!!==== 明天掛賣一波 =====!!!")
            
    if buy_OB == False and MA1[i] > MA2[i]:
        preDay = 1
        while MA1[i-preDay] == MA2[i-preDay]:
            preDay += 1
        if MA1[i-preDay] < MA2[i-preDay]:
            buy_OB = True
            Risk = 0
            Oppt = 0
            buyInReady = False
            buyInPrice = Decimal(str(PriceWay[i]))
            print("---=== 執行BUY OB 觀察日 ===---")

    if sell_OB == False and Stocks and MA1[i] < MA2[i]:
        preDay = 1
        while MA1[i-preDay] == MA2[i-preDay]:
            preDay += 1
        if MA1[i-preDay] > MA2[i-preDay]:
            sell_OB = True
            Risk = 0
            Oppt = 0
            sellOutReady = False
            sellOutPrice = Decimal(str(PriceWay[i]))
            print("---=== 執行SELL OB 觀察日 ===---")



print("手上的股票有：", len(Stocks)," 張，分別為：", end='')
for Stock in sorted(Stocks):
    print(Stock, end=', ')
print()
print("總賣出價錢", Cost + Profit)
print("獲利：", Profit)
print("成本(總賣出價錢 - 獲利)：", Cost)

