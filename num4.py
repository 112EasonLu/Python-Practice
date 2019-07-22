from random import randint
ra=randint(10**1000, 10**1001)
inp=str(ra)
print(len(inp))
#import time
#tStart = time.time()#計時開始
#inp=input('number:')

if len(inp)%2!=0:
	inp=str(10*int(inp))
length=len(inp)
a=0
for i in range(1,length+1,2):
	a+=int(inp[i])-int(inp[i-1])
print(abs(a))

#tEnd = time.time()#計時結束
#列印結果
#print ("It cost %4f sec" %(tEnd - tStart))#會自動做近位
#print (tEnd - tStart)#原型長這樣