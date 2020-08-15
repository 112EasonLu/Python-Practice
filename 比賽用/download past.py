from urllib.request import urlretrieve
import os

#前處理
year=[]
for i in range(2000,2017):
    year.append(str(i))

#命名奇怪但有規則，我們慢慢做吧 XDD
s=list(map(lambda x: x+'s', year))
f=list(map(lambda x: x+'f', year)) #lambda 是一個迭代的函數，所以我們要在用list轉一次變成list
hs,hf=[],[]

url='http://web.cs.nthu.edu.tw/ezfiles/15/1015/img/3368/' #url
path==os.getcwd() + '/test' #"/Users/luyisheng/Desktop/NCHU" #資料夾位置記得改一下

for i in range(len(f)):
    hs.append(url+s[i]+'.rar')
    hf.append(url+f[i]+'.rar')

hf.pop()#Fuck you 2016開始分裂
f.pop()
print("Fuck you after 2016 Fall")
total=hs+hf
name=s+f

#創立資料夾
if (os.path.exists(path) == False): #判斷資料夾是否存在
    os.makedirs(path) #Create folder

#using .rar   
for i in range(len(total)):
    urlretrieve(total[i], path+"/{}.rar".format(name[i]))

#檔案類型不同..只能再for一次...using .7z  
other=['2016Fall','2017Fall','2017Spring','2018Spring']  
for i in range(len(other)):
    urlretrieve(url+other[i]+'.7z', path+"/{}.7z".format(other[i])) 

print ("OH!Yes!尻了吧")