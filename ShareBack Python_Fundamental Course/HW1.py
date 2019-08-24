import math

def ask():
	tyPe={"a":"紅茶","b":"綠茶","c":"奶茶"}
	size={"a":"中杯","b":"大杯"}
	sugar={"a":"全糖","b":"少糖","c":"無糖"}
	ice={"a":"全冰","b":"半冰","c":"去冰"}
	Set=[tyPe,size,sugar,ice]
	question=["請問你要什麼飲料：a:紅茶,b:綠茶,c:奶茶","請問你要的大小是：a:中杯,b:大杯","請問你的甜度是：a:全糖,b:少糖,c:無糖","請問你的冰塊是：a:全冰,b:半冰,c:少冰"]
	drinkname=[]
	for i in range(4):
		print(question[i])
		check=input()
		if check in Set[i]:
			drinkname.append(Set[i][check])
		else:#當輸入引述不在dict中時，先存-1於list中，回傳後方便判斷
			drinkname.append(-1) 
			break
	return answer#ask customers what he want

def Price(drink,num):
	price1={"紅茶中杯":25,"綠茶中杯":25,"綠茶大杯":30,"紅茶大杯":30,"奶茶中杯":35,"奶茶大杯":50}
	return num*price1[drink]#is the cost of drinks which customers bought

def recy(cup): #is the discount of the cup due to environment friendly
	print("請問您自備幾個環保杯(每杯折讓2元)：")
	check_recy=int(input())
	if check_recy <=cup:
		recy_price=check_recy*2
	else:
		recy_price=cup*2
	return recy_price

def bag(cup): #is the cost of the bag
	print("你需要袋子嗎(2元/pc)？ 需要(每袋裝6杯，少於6杯以6杯計)：1,不需要：0")
	check_bag=input()
	if check_bag=="1":
		bag_number=(math.ceil(cup/6))*2
	else:
		bag_number=0
	return bag_number

#------------I'm main, I'm man.------------
drinkname=ask()
if -1 in drinkname:#Once -1 exists in the list, program return "error"
	print("Sorry....你的輸入有錯誤，你要的飲料不存在這個空間喔")
else:
	print("請問你要幾杯")
	cup=int(input())

	drink=drinkname[0]+drinkname[1]#to use in dict
	drink_print=drinkname[0]+drinkname[1]+drinkname[2]+drinkname[3]# papring for print
	
	#Counting cost
	drink_origin_price=Price(drink,cup)
	bag_price=bag(cup)
	envir_discount=recy(cup)
	Total=drink_origin_price+bag_price-envir_discount

	print("你的飲料是{}杯{}，需要{}個袋子，使用環保杯共可折讓{}元，最後總共是{}元。".format(cup,drink_print,int(0.5*bag_price),envir_discount,Total))