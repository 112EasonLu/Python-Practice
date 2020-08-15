#How to use list
L=[1,2,3,4,5]
print(L)
L.append(6)
print(L)
L.pop(2)
print(L)
del(L[2])# like .pop(index)
print(L)
#print(L[0])

for number in L:
	#print(number)
	print("Number:{}".format(number))

#Note: 這是將L裡面的每一個element抓出來，而非index抓出該位置的東西




text.py中的內容如下
def bla():
	........(1)

if __name__ == '__main__':
	bla()



意思是當我執行某一個*.py檔案時(Example: $python text.py)，
『__name__ ='__main__'(__name__ 被assign'__main__')』
此時檔案中的『if __name__ == '__main__'』是指
當我的'__main__'== '__main__'滿足下，會開始執行bla()