# 自動爬取網頁，並以 selenium 自動定位欲擷取的特定文字，螢幕截圖， OpenCV 辨識文字，
## 將所辨識文字自動填表到指定網頁表單
from selenium import webdriver
import time
import os
import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
import pytesseract
import pymysql
import datetime

# 調整對比度的函式
def modify_contrast_and_brightness2(img, brightness , contrast):
    import math
    
    B = brightness / 255.0
    c = contrast / 255.0 
    k = math.tan((45 + 44 * c) / 180 * math.pi)

    img = (img - 127.5 * (1 - B)) * k + 127.5 * (1 + B)
      
    # 所有值必須介於 0~255 之間，超過255 = 255，小於 0 = 0
    img = np.clip(img, 0, 255).astype(np.uint8)

    # # 呈現圖片
    # plt.imshow(img)
    # plt.show()

# 預備 - 圖片下载資料夾
folder = 'ntc_image'
if not os.path.exists(folder):
    os.mkdir(folder)
    print('文件不存在，已創建')
else:
    print('準備下載圖片')

url = 'https://ntc.im/pn/'
user_agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Mobile Safari/537.36'
option = webdriver.ChromeOptions()
option.add_argument('user-agent='+ user_agent)
# option.add_argument('--headless')
driver = webdriver.Chrome(options=option)
driver.get(url)
time.sleep(4)
# driver.execute_script('window.scrollTo(,document.body.scrollHeight)')
#放大視窗
# driver.maximize_window()
# time.sleep(2)

# 獲取圖片檔名 .location_once_scroll_into_view
element = driver.find_element_by_xpath('//*[@id="intro"]/div/div[1]/div/h2')
img_name = element.text[:5]
print(f'圖片-{img_name}-位置已找到')

# 移動到指定文字處
# element.click()
element.location_once_scrolled_into_view
time.sleep(2)

# 放大瀏覽器比例以擷取大一點的圖片提高文字辨識度
# zoom_in = "document.body.style.zoom='1.25'"
# driver.execute_script(zoom_in)
# time.sleep(1)
# 擷取指定圖片並儲存
img_path = f"ntc_image/{img_name}.png"
if not os.path.exists(img_path):
    driver.get_screenshot_as_png(img_path)
    print('圖片不存在，已創建')
else:
    orig = Image.open(img_path)
    orig.save(img_path, 'png', optimize=True, quality = 95)
    print('指定圖片已更新')

time.sleep(3)
# 用 Pillow 裁切圖片
webpage=Image.open(img_path)
# left,upper= 230, 530
# right,bottom=left+330,upper+69 #定四個頂點的比特位置
image_crop=webpage.crop(box=(228,530,552,600))
img_cropped = 'img_cropped.png'
if not os.path.exists(img_cropped):
    image_crop.save(img_cropped, optimize=True, quality = 95)
else:
    image_crop.save(img_cropped, quality = 95)
    print('裁切圖片已更新')

img_cropped_path = rf'{os.path.abspath(img_cropped)}'

# 關閉瀏覽器
driver.close()

# 影像灰階 -> 二值化
img = cv2.imread(img_cropped)
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# ret, img_binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

# 辨識圖片文字
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\hsiao\.conda\envs\data_visual\Lib\Tesseract-OCR\tesseract.exe'
##　讀取第一行
line1 = pytesseract.image_to_string(img, lang='chi_tra')
line1 = line1.split('\n')[0].replace(' ','')
print(line1)

## 灰階化後，讀取第二行
line2 = pytesseract.image_to_string(img_gray, lang='chi_tra')
line2 = line2.split('\n')[1].replace(' ','')
print(line2)

## 合併兩行文字
text_final = line1 + line2

# 儲存文字到 My SQL
#資料庫連線設定
#可縮寫db = pymysql.connect("localhost","root","root","db=30days" )
conn = pymysql.connect(
    host='localhost', port=3306, 
    user='root', passwd='dc0906708652', charset='utf8'
    )

# 建立操作游標
cursor1 = conn.cursor()

# 建立資料庫(如果資料庫存在就不建立，防止異常)
sql1 = """CREATE DATABASE IF NOT EXISTS ntc ;"""
cursor1.execute(sql1)

# 連線到新建資料庫
db = pymysql.connect(
    host='localhost', port=3306, 
    user='root', passwd='dc0906708652', 
    db='ntc',charset='utf8'
    )

cursor2 = db.cursor()

# 建立 table
sql2 = """
CREATE TABLE IF NOT EXISTS ntc_hh (
    _id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    String VARCHAR(255), 
    Image VARCHAR(255), 
    UpdateTime VARCHAR(255)
    );
"""
cursor2.execute(sql2)


Now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
sql3 = f"""
REPLACE INTO ntc.ntc_hh(String, Image, UpdateTime) 
VALUES ('{str(line1)}', '{rf'{os.path.abspath(img_cropped)}'}', '{str(Now)}');
"""
# format(line1, img_cropped_path,str(Now))

# 將字串與圖片路徑存入 MySQL
cursor2.execute(sql3)

# 取出資料庫內資料
sql4 = """
SELECT String FROM ntc_hh"""

cursor2.execute(sql4)
# 將選取的資料用 fetchone() 存到變數裡
str2post = cursor2.fetchone()

sql5 = """
SELECT Image FROM ntc_hh"""

cursor2.execute(sql5)

imgPath2post = cursor2.fetchall()


# 自動提交資料
url2 = 'https://ntc.microtrend.tw/202202?classid=DV101&studentid=20'
header = {"User-Agent": user_agent}

option = webdriver.ChromeOptions()
option.add_argument('user-agent='+ user_agent)
# option.add_argument('--headless')
driver2 = webdriver.Chrome(options=option)
driver2.get(url2)

input_ele = driver2.find_element_by_xpath('//*[@id="handover"]/div/div/div/form/div[2]/div/div/div/div/font')

js = """
var i = document.createElement('input');
i.setAttribute("type", "text");
i.setAttribute("class", "form-control border-0 border-bottom");
i.setAttribute("name", "anwser");
i.setAttribute("id", "anwser");
i.setAttribute("value", "{}");
var target_ele = arguments[0];
target_ele.insertAdjacentElement("afterend", i);
""".format(line1)
driver2.execute_script(js, input_ele)
driver2.find_element_by_id("img_src").send_keys(r"C:\Users\hsiao\OneDrive\2022_SCE\proj_HH\img_cropped.png")


## 上傳圖片路徑

time.sleep(2)
img_up_element = driver2.find_element_by_id("img_src")
img_up_element.send_keys(os.path.abspath(img_cropped))

# 點擊資料上傳
botton = driver2.find_element_by_xpath('//*[@id="handover"]/div/div/div/form/div[4]/div/button')
botton.click()
time.sleep(2)
driver2.close()



# # 自動填寫表單
# url2 = 'https://ntc.microtrend.tw/202202?classid=DV101&studentid=20'
# header = {"User-Agent": user_agent}

# option = webdriver.ChromeOptions()
# option.add_argument('user-agent='+ user_agent)
# # option.add_argument('--headless')
# driver2 = webdriver.Chrome(options=option)

# ## 上傳圖片路徑
# driver2.get(url2)
# time.sleep(2)
# img_up_element = driver2.find_element_by_id("img_src")
# img_up_element.send_keys(os.path.abspath(img_cropped))

# # Selenium 執行 javascript 修改html
# insertInput = """
#     var i = document.createElement('input');
#     i.setAttribute("type", "text");
#     i.setAttribute("class", "form-control border-0 border-bottom");
#     i.setAttribute("name", "str2post");
#     i.setAttribute("id", "str2post");
#     i.setAttribute("PlaceHolder", "ocr_text");
#     i.setAttribute("value", "你不需要很厲害才能開始");
#     var inputContainer = document.getElementByXPath('//*[@id="handover"]/div/div/div/form/div[2]/div/div/div/div/font');
#     inputContainer.insertAdjacentElement("afterend", i)

#     """       
# # input_locate = driver.find_element_by_xpath('//*[@id="handover"]/div/div/div/form/div[2]/div/div/div/div/font')
# driver2.execute_script(insertInput)
# # driver2.find_element_by_id('str2post').send_keys(line1)

# # 點擊資料上傳
# botton = driver2.find_element_by_xpath('//*[@id="handover"]/div/div/div/form/div[4]/div/button')
# botton.click()
# driver2.close()
# # res = requests.get(url2, headers=header)
# soup = BeautifulSoup(res.text, 'html.parser')
# def addTag(html):
  
#     # parse html content
#     # soup = BeautifulSoup(html, "html.parser")
  
#     # create new tag
#     # Here we are creating a new div
#     new_input_tag = soup.new_tag('input')
#     new_input_tag['class'] ="form-control border-0 border-bottom"
#     new_input_tag['type'] = "text"
#     new_input_tag['name'] = "str2post"
#     new_input_tag['id'] = "str2post"
#     new_input_tag['value'] = str2post

#     # # Adding content to div
#     # new_div.string = " This is new div "
  
#     # Inserting new tag before anchor point
#     anchor = soup.find('/html/body/div[1]/div[1]/div/div/div/form/div[2]/div/div/div/div/span')
#     soup.html.body.div.insert_before(anchor)

#     # Printing the modified object
#     print(soup)
  
  
# # Function Call
# addTag()
# # 新增 input 標籤

