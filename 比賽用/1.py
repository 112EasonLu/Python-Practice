#a=["q","w","e","r"]
##创建一个空字典
#b=dict()
##这里i表示的是索引，item表示的是它的值
#for i,item in enumerate(a):
#    b[i]=item
#print(b)#


year=[]
for i in range(2010,2017):
    year.append(str(i))

s=list(map(lambda x: x+'s', year))
f=list(map(lambda x: x+'f', year))
hs,hf=[],[]
for i in range(len(f)):
    hs.append('http://web.cs.nthu.edu.tw/ezfiles/15/1015/img/3368/'+s[i]+'.rar')
    hf.append('http://web.cs.nthu.edu.tw/ezfiles/15/1015/img/3368/'+f[i]+'.rar')
print(hs)
print(hf)