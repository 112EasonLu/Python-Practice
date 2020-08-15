#import requests,os
#from bs4 import BeautifulSoup
#from urllib.request import urlopen
##from urlparse import urljoin
#
#url = 'http://academic.ntue.edu.tw/files/11-1007-467.php'
#html = requests.get(url)
#html.encoding='utf-8'
#
#
#sp=BeautifulSoup(html.text,"html.parser")
#
##建立目錄
#pdf_dir="pdfs/"
#if not os.path.exists(pdf_dir):
#     os.mkdir(pdf_dir)
#
#
#links=sp.find_all("a")
#for link in links:
#  href=link.get("href")
#  #不用再多一層 attr 迴圈，href 已經是連結了
#  
#  #如果不是 .pdf 結尾，直接跳過不處理
#  if(href == None or href.split('.')[-1]!='pdf'):
#    continue;
#  
#  #關於網址的處理
#  if(href[0:4]=='http'):
#    full_path = href
#  elif(href[0]=='/'): #這邊要處理開頭為 / 的網址
#    full_path = "http://academic.ntue.edu.tw" + href
#  else: #其他的是相對路徑
#    full_path= "http://academic.ntue.edu.tw/files/" + href
#  print(full_path)
#  
#  #後面就是抓 full_path 並儲存#


import urllib
from urllib.request import urlretrieve
import requests
import os
import rarfile
#url = 'http://www.blog.pythonlibrary.org/wp-content/uploads/2012/06/wxDbViewer.zip'

year=[]
for i in range(2000,2017):
    year.append(str(i))

s=list(map(lambda x: x+'s', year))
f=list(map(lambda x: x+'f', year))
hs,hf=[],[]
for i in range(len(f)):
    hs.append('http://web.cs.nthu.edu.tw/ezfiles/15/1015/img/3368/'+s[i]+'.rar')
    hf.append('http://web.cs.nthu.edu.tw/ezfiles/15/1015/img/3368/'+f[i]+'.rar')
hf.pop()
urll='http://web.cs.nthu.edu.tw/ezfiles/15/1015/img/3368/'
path="/Users/luyisheng/Desktop/NCHU"

if (os.path.exists(path) == False): #判斷資料夾是否存在
        os.makedirs(path) #Create folder




def down(url,i):
  #print ("downloading with urllib")
    urlretrieve(url, path+"/{}.rar".format(i))
#    rar_name = path+"/{}.rar".format(i)
#    cur_path = os.getcwd()
#    CompressionSite = path
#    os.chdir(CompressionSite)
#    rar = rarfile.RarFile(rar_name) 
#    print(rar.namelist())
#    rar.extractall()
#    rar.close()
#    os.chdir(cur_path)
    #with ZipFile(open(path+"/{}.zip".format(i), 'rb')) as f:
     #   f.extractall(".")
#rarfile不支持创建rar压缩卷,请用zip/7z

if __name__ == '__main__':

    for i in range(len(hs)):
        down(hs[i],s[i])
    for i in range(len(hf)):
        down(hf[i],f[i])
    other=['2016Fall','2017Fall','2017Spring','2018Spring']  
    for i in range(len(other)):
        urlretrieve(urll+other[i]+'.7z', path+"/{}.7z".format(other[i])) 
    #file.close()    
    print ("down")

#print ("downloading with requests")
#r = requests.get(url)
#with open("code3.zip", "wb") as code:
#    code.write(r.content)

