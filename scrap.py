#import requests
#from bs4 import BeautifulSoup 
#r = requests.get("https://www.ptt.cc/bbs/MobileComm/index.html") #將此頁面的HTML GET下來
#soup = BeautifulSoup(r.text,"html.parser") #將網頁資料以html.parser
#sel = soup.select("div.title a") #取HTML標中的 <div class="title"></div> 中的<a>標籤存入sel
#for s in sel:
#    print(s["href"], s.text)


#import requests
#from bs4 import BeautifulSoup
#r = requests.Session()
#payload ={
#    "from":"/bbs/Gossiping/index.html",
#    "yes":"yes"
#}
#r1 = r.post("https://www.ptt.cc/ask/over18?from=%2Fbbs%2FGossiping%2Findex.html",payload)
#r2 = r.get("https://www.ptt.cc/bbs/Gossiping/index.html")
#
#soup = BeautifulSoup(r.text,"html.parser") #將網頁資料以html.parser
#sel = soup.select("div.title a") #取HTML標中的 <div class="title"></div> 中的<a>標籤存入sel
#for s in sel:
#    print(s["href"], s.text)

#import requests
#pic=requests.get('https://imgur.dcard.tw/N2k5kV2m.jpg') #圖片網址
#img2 = pic.content #圖片裡的內容
#pic_out = open('img1.png','wb') #img1.png為預存檔的圖片名稱
#pic_out.write(img2) #將get圖片存入img1.png
#pic_out.close() #關閉檔案(很重要)

import requests
import urllib.request
from bs4 import BeautifulSoup
import os
import time

url = 'https://www.google.com/search?safe=off&biw=1280&bih=689&tbm=isch&sxsrf=ACYBGNQFse93OpEVTF9qhReEPI9tREigFg%3A1567742344615&sa=1&ei=iNlxXZ2YJfKbmAX-_quADA&q=naked+girl&oq=naked+girl&gs_l=img.3...868.8396..8709...3.0..0.78.417.8......0....1..gws-wiz-img.......0j0i67.Lb028-BKW-M&ved=0ahUKEwid_LKsp7vkAhXyDaYKHX7_CsAQ4dUDCAY&uact=5'

photolimit = 20

headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url,headers = headers) #使用header避免訪問受到限制
soup = BeautifulSoup(response.content, 'html.parser')
items = soup.find_all('img')
folder_path ='./photo/'

if (os.path.exists(folder_path) == False): #判斷資料夾是否存在
    os.makedirs(folder_path) #Create folder

for index , item in enumerate (items):

    if (item and index < photolimit ):
        html = requests.get(item.get('src')) # use 'get' to get photo link path , requests = send request
        img_name = folder_path + str(index + 1) + '.png'

        with open(img_name,'wb') as file: #以byte的形式將圖片數據寫入
            file.write(html.content)
            file.flush()

        file.close() #close file
        print('第 %d 張' % (index + 1))
        time.sleep(1)

print('Done')