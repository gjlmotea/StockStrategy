import time
today = time.strftime("%Y%m")

stockNo = input("請輸入欲爬取的股票代號：")
print()
dateStart = input("預設爬取全部歷史資料，\
                   \n否則輸入欲爬取的日期 起始月份(ex:201904)：\
                   \n")

dateEnd = today
if dateStart.lower() == '':
    dateStart = "201001"
else:
    if dateStart.lower() < '201001':
        while dateStart.lower() < '201001':
            dateStart = input("起始月份須為201001以後，請再輸入一次。\n")
        while dateStart.lower() > today:
            dateStart = input("起始月份不可大於今日，請再輸入一次。\n")
    print()
    dateEndInput = input("請輸入爬取日期結束月份(ex:202003)\
                     \n預設為今天：\
                     \n")
    if dateEndInput:
        if dateEndInput.lower() < '201001':
            while dateEndInput.lower() < dateStart:
                dateEndInput = input("結束月份須大於起始月份，請再輸入一次。\n")
            while dateEndInput.lower() > today:
                dateEndInput = input("結束月份不可大於今日，請再輸入一次。\n")    
        dateEnd = dateEndInput



import csv
import requests
import time
from bs4 import BeautifulSoup

response = requests.session()
def getResponse(year, month, date = '01'):
    Ymd = str(year) + str(month) + str(date)
    url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY?stockNo=" + str(stockNo) + "&date=" + str(Ymd)
    print(url)
    res = response.get(url)
    return res

def getYear(date):
    return int(date[0:4])

def getMonth(date):
    return int(date[4:6])

def dateToStr(date):
    if date < 10: #Leading Zero
        return '0' + str(date)
    return str(date)



def saveToCsv(json, outputFileName):
    stat = json['stat']
    title = [json['title']]
    fields = json['fields']
    data = json['data']
    notes = json['notes']
    with open(dataPath + outputFileName + '.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(title)
        writer.writerow(fields)
        for d in data:
            writer.writerow(d)
        writer.writerow(["說明:"])
        for i in range(len(notes)):
            writer.writerow([notes[i]])


def createDirectory(dataPath):
    import os
    try:
        os.mkdir(dataPath)
    except OSError:
        print("資料夾已存在。")
    except Exception:
        print("路徑有誤...")
    else:
        print("成功建立" + dataPath +"資料夾。")

def deleteDirectory(dataPath):
    import shutil
    while True:
        try:
            shutil.rmtree(dataPath)
        except OSError:
            print("找不到" + dataPath + "目的資料夾。")
            break
        except IOError:
            print("請先關閉所有" + dataPath + "資料夾底下的檔案。")
            time.sleep(3)
        except Exception:
            print("發生其他未知錯誤。")
        else:
            print("已清除" + dataPath + "資料夾及底下的所有檔案。")
            break

if __name__ == '__main__':
    dataPath = "./data/"
    deleteDirectory(dataPath)
    createDirectory(dataPath)
    for year in range(getYear(dateStart), getYear(dateEnd)+1):
        month = 1
        monthUpper = 12
        if year == getYear(dateEnd):
            monthUpper = getMonth(dateEnd)
        if year == getYear(dateStart):
            month = getMonth(dateStart)

        while month <= monthUpper:
            res = getResponse(year, dateToStr(month))
            if res.status_code != 200:
                print("與網站的連線出現錯誤...", "該資料日期:", year, month)
                continue
            json = res.json()
            if json['stat'] != 'OK':
                print("無法成功抓取資料!! :", json['stat'], "該資料日期:", year, month)
            outputFileName = "STOCK_DAY" + str(year) + dateToStr(month)
            saveToCsv(json, outputFileName)
            time.sleep(2.5)
            month += 1

#print(getResponse())
