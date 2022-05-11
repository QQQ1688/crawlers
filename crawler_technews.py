#Py - 爬蟲 - 作業1 - Technews
## 自動爬取新聞網頁，將標題、內文自動存成 txt 檔案
import requests
from bs4 import BeautifulSoup
import json

url = 'https://technews.tw/'
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'}

resp = requests.get(url, headers=header)
print(resp.status_code)
soup = BeautifulSoup(resp.text, 'html.parser')

block_soups = soup.find_all('li', {'class':'block2014'})
final_lst = []

for block in block_soups:
    # category 類別
    category = block.find('div', {'class': 'cat01'}).text

    #總標題
    sum_title = block.find('div', {'class':'sum_title'}).text.strip()

    #總標題連結
    sum_title_url = block.find('div', {'class': 'img'}).find('a').get('href')
    text_resp = requests.get(sum_title_url, headers=header)
    text_soup = BeautifulSoup(text_resp.text, 'html.parser')
    # 選取有總標題文章內文標籤下的所有內文 p 標籤 
    text = text_soup.find('div', {'class': 'indent'}).find_all('p')
    # 如果 p 標籤下是真的有內文的，則將所有內文存進一個 list
    text_list = []
    for p in text:
        if p.text == '':
            continue
        else:
            text_list.append(p.text)
    #總標題文章內文利用 writelines(list) 寫入並存檔
    with open(f'sum_{category}_{str(sum_title[:4])}.txt', 'w', encoding = "utf-8") as file:
        file.writelines(text_list)
        file.close()


    #次標題 & 次連結
    spotlist = []
    for i in range(0, 3):
        # 擷取次標題在每個 block 下的文字
        spot_category = block.find('div', {'class': 'cat01'}).text
        # 利用 select() 方法選取 class=itemelse 下列表格式 (ul) 下的所有 li，並利用 i 當迴圈的 index
        # 利用 strip() 將抓取的標題兩邊清乾淨
        title = block.select('.itemelse li')[i].get_text().strip()
        # 抓取 a 標籤下 href 屬性的值，以獲得 url 連結
        spot_url = block.select('.itemelse li')[i].find('a').get('href')
        # 將 title & url 利用字典資料形式進行鍵值配對，並存到 spotlist 成為一個 list
        spot = {'title': title, 'url': spot_url}
        spotlist.append(spot)
        #次標題連結內文
        # 利用 request.get() 向次標題連結所在網站請求內容
        spot_resp = requests.get(spot_url, headers=header)
        spot_soup = BeautifulSoup(spot_resp.text, 'html.parser')
        # 抓取次標題連結網站內的內文
        spot_text = spot_soup.find('div', {'class': 'indent'}).find_all('p')
        spot_text_list = []
        for p in text:
            if p.text == '':
                continue
            else:
                spot_text_list.append(p.text)
        #次標題內文寫入 & 存檔
        with open(f'spot_{spot_category}_{str(title[:4])}.txt', 'w', encoding = "utf-8") as file:
            file.writelines(text_list)
            file.close()


    final_lst.append({
        'category': category,
        'sum_title': sum_title,
        'sum_title_url' : sum_title_url,
        'spotlist' : spotlist
    })



with open('Exam1_1.json', 'w') as f:
    json.dump(final_lst, f)

f.close()
 
