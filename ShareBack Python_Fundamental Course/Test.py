#quantity={int}
#a=int(input())
#print(type(a))
#if a in quantity:
#	print("OK")
#else: print("GG")
import math

def set1():
	tyPe={"a":"紅茶","b":"綠茶","c":"奶茶"}
	size={"a":"中杯","b":"大杯"}
	Babo={"a":"加珍珠","b":""}
	sugar={"a":"全糖","b":"少糖","c":"無糖"}
	quantity=set(range(1,100))
	more={"a":1,"b":0}

	return tyPe,size,sugar,ice,quantity,more

def ask():
	k=True
	tyPe,size,sugar,ice,quantity,more=set1()
	Set=[tyPe,size,sugar,ice,quantity,more]
	question=["請問你要什麼飲料：a:紅茶,b:綠茶,c:奶茶",
	"請問你要的大小是：a:中杯,b:大杯",
	"請問你的甜度是：a:全糖,b:少糖,c:無糖",
	"請問你的冰塊是：a:全冰,b:半冰,c:少冰",
	"請問你要幾杯(請輸入整數)?",
	"請問是否還需要其他飲料：a:是,b:否"]
	drinkname=[]
	current_order=[]
	for i in range(4):
		print(question[i])
		check=input()
		if check in Set[i]:
			current_order.append(Set[i][check])
		else:#當輸入引述不在dict中時，先存-1於list中，回傳後方便判斷 
			k=False

	print(question[4])
	check=input()
	if check.isdigit():
		current_order.append(int(check))
	else:#當輸入引述不在dict中時，先存-1於list中，回傳後方便判斷
		k=False

	print(question[5])
	check=input()
	if (check in Set[5]) and k:
		k=True
	else:
		k=False
	drinkname=current_order
	return drinkname,k,te #ask customers what he want


test=True
te=1
parameter,drinkname=[],[]
while test and te:
	drinkname_pre,test,te=ask()
	#print(drinkname_pre,l,test)
	parameter.append(test)
	#print(drinkname_pre)
	drinkname.append(drinkname_pre)

if test==False:#Once -1 exists in the list, program return "error"
	print("Sorry....你的輸入有錯誤，你要的飲料可能不存在這個空間喔!!!")

else:print("OK")
