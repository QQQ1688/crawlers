from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import requests
import os
import random
import time
import pandas as pd
import numpy as np
import pymysql

wang = ['王品牛排', '西堤', '陶板屋', '原燒', 
'聚北海道', '藝奇', '夏慕尼', '品田牧場', '石二鍋', 
'hot 7', 'hot7', '莆田', '青花椒', '享鴨', '丰禾', '樂越', 
'12MINI', 'THE WANG', '和牛涮', '尬鍋', '肉次方 燒肉放題', 
'王品嚴選', '王品瘋美食']

han = ['漢來海港', '漢來名人坊', '漢來蔬食', '漢來軒', '翠園粵菜', 
'五梅先生', '安那居', '上菜', '福園台菜', '弁慶', '精緻海鮮火鍋', 
'糕餅小舖', '大廳酒廊', 'Hi Lai Café', 'Pavo', '焰 鐵板燒']

thai = ['瓦城', '非常泰', '1010湘', '大心', '時時香', '月月泰', 
'YABI KITCHEN', '十食湘']


def scrape_ifoodie(group):
    user_agent = UserAgent()
    header = {'User-Agent': user_agent.random}
    timeout = random.choice(range(80, 350))
    option = webdriver.ChromeOptions()
    option.add_argument('user-agent='+ user_agent.random   )
    option.add_argument("--disable-notifications")
    option.add_argument('--headless')
    driver = webdriver.Chrome(options=option)

    for i in range(len(group)):
        print(group[i])
        group_name = []
        brand = []
        titles = []
        stars = []
        review_nums = []
        addrs = []
        links = []

        goo_names = []
        goo_avgs = []
        goo_revs = []
        goo_cats = []
        lats = []
        longs = []
        for n in range(1, 6):
            try:
                url = f'https://ifoodie.tw/explore/list/{group[i]}?page={n}'
                print(url)
                response = requests.get(url, headers=header, timeout = timeout)

                soup_i = BeautifulSoup(response.content, "html.parser")

                # 爬取前五筆餐廳卡片資料
                cards = soup_i.find_all(
                    'div', {'class': 'jsx-558691085 restaurant-info'})
            except AttributeError:
                pass

            try:
                for card in cards:
                    check_title = card.find("a", {"class": "jsx-558691085 title-text"}).getText()
                    # 如果餐廳確為搜索餐廳，則進入其葉面並爬取資料
                    if str(group[i]) in check_title: 
                        # # 餐廳名稱
                        # title = card.find("a", {"class": "jsx-558691085 title-text"}).getText()
                        # # 餐廳評價
                        # star = card.find(  
                        #     "div", {"class": "jsx-1207467136 text"}).getText()
                        # # 評論數
                        # review_num = card.find(   
                        #     "a", {"class": "jsx-558691085 review-count"}).getText()[1]
                        # # 餐廳地址
                        # addr = card.find(  
                        #     "div", {"class": "jsx-558691085 address-row"}).getText()
                        # # 餐廳個別網址
                        link = 'https://ifoodie.tw' + card.find(
                                "a", {"class": "jsx-558691085"}).get('href') 
                        # 延伸造訪各餐廳自己頁面 
                        res2 = requests.get(link)
                        # 獲取餐廳自己頁面網頁原始碼
                        soup2 = BeautifulSoup(res2.content,"html")
                        # 擷取餐廳自己頁面上的 google map 連結
                        goo_link = soup2.find("a", {"class":"jss76 jss50 jss52 jss55 btn btn-google"}).get('href')
                        # 造訪 google 頁面
                        driver.get(goo_link)
                        time.sleep(random.randrange(0, 8))
                        # 獲取餐廳自己頁面網頁原始碼
                        soup3 = BeautifulSoup(driver.page_source,"html")                       
                        # google 分店名稱
                        goo_name = soup3.find('h1').text. strip()
                        # google 平均星等
                        goo_avg = soup3.find("span", {"class": "aMPvhf-fI6EEc-KVuj8d"}).text
                        # google 評論數
                        goo_rev = soup3.find_all("button", {"class": "Yr7JMd-pane-hSRGPd"})[0].text
                        # google 餐廳分類 
                        goo_cat = soup3.find_all("button", {"class": "Yr7JMd-pane-hSRGPd"})[4].text
                        # google map url
                        map_url = driver.current_url
                        # 緯度
                        lat = map_url.split('/')[6].replace('@', '').split(',')[0]
                        # 經度
                        long = map_url.split('/')[6].replace('@', '').split(',')[1]
                   
                        #將取得的餐廳名稱、評價及地址連結一起，並且指派給content變數
                        # content += f"{title} \n{stars}顆星 \n{address} \n\n"
                        # group_name.append(str(group[0][:2]))
                        # brand.append(group[i])
                        # titles.append(title)
                        # stars.append(star)
                        # review_nums.append(review_num)
                        # addrs.append(addr)
                        # links.append(link)

                        goo_names.append(goo_name)
                        goo_avgs.append(goo_avg)
                        goo_revs.append(goo_rev)
                        goo_cats.append(goo_cat)
                        lats.append(lat)
                        longs.append(long)

            except AttributeError:
                pass
                    
        # df_iFoodie = pd.DataFrame({
        #     '集團': group_name,
        #     '品牌': brand,
        #     '分店': titles,
        #     '評分' : stars,
        #     '評論數': review_nums,
        #     '地址' : addrs,
        #     '分店網址': links
        #     })
        # print(df_iFoodie.head())
        # path = os.getcwd() + f"\\{str(group[0][:2])}"
        # if (os.path.exists(path) == False):
        #     os.mkdir(path)
        # df_iFoodie.to_csv(f"{path}\iFoodie_{group[i]}.csv", index=False)

        df_goog = pd.DataFrame({
            '集團': group_name,
            '品牌': brand,
            '分店': titles,
            '評分' : goo_avgs,
            '評論數': goo_revs,
            '菜系' : goo_cats,
            '經度': lats,
            '緯度':longs
            })
        print(df_goog.head())
        path = os.getcwd() + f"\\{str(group[0][:2])}_goog"
        if (os.path.exists(path) == False):
            os.mkdir(path)
        df_goog.to_csv(f"{path}\goog_{group[i]}.csv", encoding="utf-8", index=False)       

if __name__=='__main__':
    scrape_ifoodie(thai)
    scrape_ifoodie(han)
    scrape_ifoodie(wang)