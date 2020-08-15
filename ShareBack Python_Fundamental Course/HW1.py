import math

#------------Basic questions and identifications-----------
def set1():
	tyPe={"a":"紅茶","b":"綠茶","c":"奶茶"}
	size={"a":"中杯","b":"大杯"}
	sugar={"a":"全糖","b":"少糖","c":"無糖"}
	ice={"a":"全冰","b":"半冰","c":"去冰"}
	more={"a":True,"b":False}
	return [tyPe,size,sugar,ice,more]

def problems():
	Q0="請問你要什麼飲料：a:紅茶,b:綠茶,c:奶茶"
	Q1="請問你要的大小是：a:中杯,b:大杯"
	Q2="請問你的甜度是：a:全糖,b:少糖,c:無糖"
	Q3="請問你的冰塊是：a:全冰,b:半冰,c:少冰"
	Q4="請問你要幾杯(請輸入整數)?"
	Q5="請問是否還需要其他飲料：a:是,b:否"
	return[Q0,Q1,Q2,Q3,Q4,Q5]

#------------Main qusestion-----------
#------------Using k confirm program working-----------

def ask():
	k=True # 判斷要不要繼續問下去的參數
	Set=set1()
	question=problems()
	current_order=[]

#------------What drink do you want?---------
	for i in range(4):
		print(question[i])
		check=input()
		if check in Set[i]:
			current_order.append(Set[i][check])
		else:#當輸入引述不在dict中時，回傳False
			k=False

#------------How many do you need?---------
	print(question[4])
	check=input()
	if check.isdigit(): #判斷是否為數字
		current_order.append(int(check))
	else:#當輸入引述不在dict中時，回傳False
		k=False

#------------Would you want more?---------
	print(question[5])
	check=input()
	if (check in Set[4]):
		order_more=Set[4][check]
		k=True #當要繼續點餐且k=true
	else:
		k=False
	return current_order,k,order_more #ask customers what he want


#------------Check Price------------
def Price(drink):
	price1={"紅茶中杯":25,"綠茶中杯":25,"綠茶大杯":30,"紅茶大杯":30,"奶茶中杯":35,"奶茶大杯":50}
	return price1[drink]#is the cost of drinks which customers bought


#------------Final question(bags, cups)------------

def recy(cup): #is the discount of the cup due to environment friendly
	print("請問您自備幾個環保杯(每杯折讓5元)：")
	check_recy=input()
	if check_recy.isdigit(): #check input
		if int(check_recy) <=cup:
			recy_price=int(check_recy)*5
		else:
			recy_price=cup*5
	else: recy_price=False #input is not acceptable
	return recy_price

def bag(cup): #is the cost of the bag
	print("你需要袋子嗎(1元/pc)？ 需要(每袋裝6杯，少於6杯以6杯計)：1,不需要：0")
	check_bag=input()
	if check_bag=="1":
		bag_number=(math.ceil(int(cup)/6))
	elif check_bag=="0":
		bag_number=0
	else: bag_number=False #input is not acceptable
	return bag_number


#------------I'm main------------
test=True
ordermore=True
drinkname,drink=[],[]
cup,total_drink_price=0,0

while test and ordermore:
	drinkname_pre,test,ordermore=ask()
	drinkname.append(drinkname_pre)
	print(test)

if test==False:#Once -1 exists in the list, program return "error"
	print("Sorry～你的輸入有誤，你要的飲料可能不存在這個空間喔!!!")
else:
	classifi={}
	
	for i in range(len(drinkname)):
		drin=drinkname[i][0]+drinkname[i][1] # type of drink
		icesur=drinkname[i][2]+drinkname[i][3] # ice and sugar
		
		total_drink_price+=Price(drin)*drinkname[i][4] # caculating price just drink
		cup+=drinkname[i][4] # caculating total cups
		
		#classification and counting
		if drin+icesur in classifi:
			classifi[drin+icesur]=classifi[drin+icesur]+drinkname[i][4]
		else:
			classifi.setdefault(drin+icesur,drinkname[i][4])

#------------Bags and discounts------------
	bag_price=bag(cup)
	envir_discount=recy(cup)
	print(bag_price,envir_discount)

	if bag_price and envir_discount:
		Total=total_drink_price+bag_price-envir_discount

		Keys=classifi.keys()
		print("您好！你的飲料：")
		for Keys in classifi:print("{}杯{}，".format(classifi[Keys],Keys))
		print("已經準備好了！需要{}個袋子，使用環保杯共可折讓{}元，最後總共是{}元。".format(bag_price,envir_discount,Total))
	else: print("Sorry～你的輸入有誤，請您重新操作一次!!!")	