from bs4 import BeautifulSoup as soup
import requests
r_ent_div = soup.find_all('div', class_ = 'r-ent', limit = 20) #找出指定的 class class面前２０筆為我們要撈取資料
category = '[' + input('請輸入要搜尋的類別：') + ']'
i = 0

for item in r_ent_div:
    title = item.find( class_ = 'title')
    if title.find('a'): #過濾掉被刪除的文章
        s = title.find('a')
        title_text = s.string
        date = item.find('div', class_ = 'date')
        if title_text.startswith(category) :
            i = i+1
            print('#{}標題: {} 發文日期： {} \n #連結：https://www.ptt.cc{}'.format(i, title_text, date.string, s.get('href')))