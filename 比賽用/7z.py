# 下載與解壓縮 財政部財政資訊中心-全國營業(稅籍)登記資料集 http://data.gov.tw/node/9400

import urllib3 #urllib2.urlopen 

import zipfile #zipfile.ZipFile



http://web.cs.nthu.edu.tw/ezfiles/15/1015/img/3368/2011s.rar

year=[]
for i in range(2010,2017):
    year.append(str(i))

s=list(map(lambda x: x+'s', year))
f=list(map(lambda x: x+'f', year))
hs,hf=[],[]
for i in range(len(f)):
    hs.append('http://web.cs.nthu.edu.tw/ezfiles/15/1015/img/3368/'+s[i]+'.rar')
    hf.append('http://web.cs.nthu.edu.tw/ezfiles/15/1015/img/3368/'+f[i]+'.rar')
hf.pop()


def DownloadTWCompany(K):
    # 檔案下載

    downloadurl = urllib3.urlopen(K)
    zipcontent= downloadurl.read()
    with open("TWRAW.zip", 'wb') as f:
        f.write(zipcontent)
    print ("下載完成!")
    
    # 解壓縮檔案

 #   print ("資料解壓縮...")
 #   with zipfile.ZipFile(open('TWRAW.zip', 'rb')) as f:
 #       f.extractall(".")  # 解壓縮密碼1234
    
    print ("解壓縮完成!")
if __name__==__manin__:
    for i in range(len(hs)):
        DownloadTWCompany(hs[i])
    for i in range(len(hf)):
        DownloadTWCompany(hf[i])
    print('down')