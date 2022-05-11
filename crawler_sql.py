from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import sqlite3
import os

# 不要打開視窗
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

url = 'https://gogakuru.com/english/phrase/genre/180_%E5%88%9D%E7%B4%9A%E3%83%AC%E3%83%99%E3%83%AB.html?layoutPhrase=1&orderPhrase=1&condMovie=0&flow=enSearchGenre&condGenre=180&perPage=50'
driver.get(url)

# 抓取指定文字，並存成 list
elements = driver.find_elements_by_css_selector('span.font-en')

text_list = []
for ele in elements:
    text = ele.text
    text_list.append(text)

# 將 list 資料存成 df
df = pd.DataFrame({'Phrase': text_list})

# 連結資料庫，如果不存在則創建一個
conn = sqlite3.connect('eng_phrases.db') 
cursor = conn.cursor()
cursor.execute('CREATE TABLE Phrases(Phrase)')  
#建立名為Phrases的資料表，裡面有一欄叫 Phrase
conn.commit() # 送出給資料庫


# 看資料庫建在哪裡，可以用 DB brower SQLite 圖形化應用程式打開來看
print(os.path.dirname(os.path.realpath('eng_phrases.db')))

# 如果 Phrases 資料表存在，就寫入資料，否則建立資料表, 並使用 conn 連結的資料庫
# # if_exists{‘fail’, ‘replace’, ‘append’}, default ‘fail’
df.to_sql('Phrases', conn, if_exists='append', index=False) 

# 透過SQL語法讀取資料庫中的資料
phrases_df = pd.read_sql("SELECT * FROM Phrases", conn)
print(phrases_df)

# 操作完後把資料庫關起來
conn.close()


# pickle - 'wb', 'rb'
import pickle

with open('Exam3.pickle', 'wb') as f:
    pickle.dump(text_list, f)

with open('Exam3.pickle', 'rb') as f:
    new_dict = pickle.load(f)

print(new_dict)