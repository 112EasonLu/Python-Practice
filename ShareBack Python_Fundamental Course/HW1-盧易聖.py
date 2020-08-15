import math

#------------Basic questions and identifications-----------
def set1():
	tyPe={"a":"紅茶","b":"綠茶","c":"奶茶"}
	size={"a":"中杯","b":"大杯"}
	Babo={"a":"加珍珠","b":""}
	sugar={"a":"全糖","b":"少糖","c":"無糖"}
	ice={"a":"全冰","b":"半冰","c":"去冰"}
	more={"a":True,"b":False}
	return [tyPe,size,Babo,sugar,ice,more]

def problems():
	Q0="請問你要什麼飲料：a:紅茶,b:綠茶,c:奶茶"
	Q1="請問你要的大小是：a:中杯,b:大杯"
	Q2="請問你要加珍珠嗎：a:加,b:不加"
	Q3="請問你的甜度是：a:全糖,b:少糖,c:無糖"
	Q4="請問你的冰塊是：a:全冰,b:半冰,c:少冰"
	Q5="請問你要幾杯(請輸入整數)?"
	Q6="請問是否還需要其他飲料：a:是,b:否"
	return[Q0,Q1,Q2,Q3,Q4,Q5,Q6]

#------------Main qusestion-----------
#------------Using k confirm program working-----------

def ask():
	k=True # 判斷要不要繼續問下去的參數
	Set=set1()
	question=problems()
	current_order=[]

#------------What drink do you want?---------
	for i in range(5):
		print(question[i])
		check=input()
		if check in Set[i]:
			current_order.append(Set[i][check])
		else:#當輸入引述不在dict中時，回傳False
			k=False

#------------How many do you need?---------
	print(question[5])
	check=input()
	if check.isdigit(): #判斷是否為數字
		current_order.append(int(check))
	else:#當輸入引述不在dict中時，回傳False
		k=False

#------------Would you want more?---------
	print(question[6])
	check=input()
	if (check in Set[5]):
		order_more=Set[5][check]#當要繼續點餐order_more=True，不點餐order_more=False
	else:
		order_more=False
		k=False
	return current_order,k,order_more #ask customers what he want

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
		bag_cost=(math.ceil(int(cup)/6))
	elif check_bag=="0":
		bag_cost=0
	else: 
		bag_cost=False #input is not acceptable
	return bag_cost


#------------Caculate cost------------
def Price(drink,babo_check):
	price1={"紅茶中杯":25,"綠茶中杯":25,"綠茶大杯":30,"紅茶大杯":30,"奶茶中杯":35,"奶茶大杯":50}
	babo={25:5,30:10,35:0,50:0}
	if babo_check=="加珍珠":
		babo_price=babo[price1[drink]]
	else: babo_price=0
	return (price1[drink]+babo_price)#is the cost of drinks which customers bought

#------------Classification and statistics------------
def classification(drinklist): #is classification and statistics of various beverages.
	cup,total_drink_price=0,0
	collection={}
	
	for i in range(len(drinklist)):
		beverages_mainname=drinklist[i][0]+drinklist[i][1] # type of drink
		icesur=drinklist[i][2]+drinklist[i][3]+drinklist[i][4] # ice and sugar
		
		# caculating price just drink
		total_drink_price+=Price(beverages_mainname,drinklist[i][2])*drinklist[i][5] 
		# caculating total cups
		cup+=drinklist[i][5] 
		
		#classification and counting
		if (beverages_mainname+icesur in collection):
			collection[beverages_mainname+icesur]=collection[beverages_mainname+icesur]+drinklist[i][5]
		elif (not (beverages_mainname+icesur in collection)) and drinklist[i][5]!=0:
			collection.setdefault(beverages_mainname+icesur,drinklist[i][5])
	return collection,cup,total_drink_price


#------------This is main.------------
test,ordermore=True,True
drinkname=[]

while test and ordermore:#ordermore means continue to order; test is used to confirm input is acceptable.
	drinkname_pre,test,ordermore=ask()
	drinkname.append(drinkname_pre)

if test==False:#Once test is False, program ends and returns "error info.".
	print("Sorry～你的輸入有誤，你要的飲料可能不存在這個空間喔!!!")
else: #classification and statistics
	beverages_class,cup,total_drink_price=classification(drinkname)

#------------Bags and discounts------------
	bag_price=bag(cup)
	envir_discount=recy(cup)

	if bag_price and envir_discount:# confirm that bag_price and envir_discount aren't false.
		Total=total_drink_price+bag_price-envir_discount

		Keys=beverages_class.keys()
		print("您好！你的飲料：")
		for Keys in beverages_class:print("{}杯{}，".format(beverages_class[Keys],Keys))
		print("已經準備好了！需要{}個袋子，使用環保杯共可折讓{}元，最後總共是{}元。".format(bag_price,envir_discount,Total))
	else: print("Sorry～你的輸入有誤，請您重新操作一次!!!") # once bag_price or envir_discount is false.