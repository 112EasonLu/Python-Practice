import math

def ask():
	tyPe={"a":"紅茶","b":"綠茶","c":"奶茶"}
	size={"a":"中杯","b":"大杯"}
	sugar={"a":"全糖","b":"少糖","c":"無糖"}
	ice={"a":"全冰","b":"半冰","c":"去冰"}
	Set=[tyPe,size,sugar,ice]
	question=["請問你要什麼飲料：a:紅茶,b:綠茶,c:奶茶","請問你要的大小是：a:中杯,b:大杯","請問你的甜度是：a:全糖,b:少糖,c:無糖","請問你的冰塊是：a:全冰,b:半冰,c:少冰"]
	answer=[0]*5
	ans=''
	for i in range(4):
		print(question[i])
		check=input()
		if check in Set[i]:
			answer[i]=Set[i][check]
		else:
			answer[i]=-1
			break
	return answer

def Price(drink,num):
	price1={"紅茶中杯":25,"綠茶中杯":25,"綠茶大杯":30,"紅茶大杯":30,"奶茶中杯":35,"奶茶大杯":50}
	return num*price1[drink]

def recy(cup):
	print("請問您自備幾個環保杯(每杯折讓2元)：")
	check_recy=int(input())
	if check_recy <=cup:
		recy_price=check_recy*2
	else:
		recy_price=cup*2
	return recy_price

def bag(cup):
	print("你需要袋子嗎？ 需要(每6杯一袋，少於6杯以6杯計)：1 不需要：0")
	check_bag=input()
	if check_bag=="1":
		bag_number=(math.ceil(cup/6))*2
	else:
		bag_number=0
	return bag_number


#####I'm main, and I'm man.#######
basic=ask()
if -1 in basic:
	print("Sorry....你的輸入有錯誤，你要的飲料不存在這個空間喔")
else:
	print("請問你要幾杯")
	cup=int(input())
	drink=basic[0]+basic[1]
	drink_print=basic[0]+basic[1]+basic[2]+basic[3]
	total_1=Price(drink,cup)
	total_2=bag(cup)
	total_3=recy(cup)
	Total=total_1+total_2-total_3
	print("你的飲料是{}杯{}，需要{}個袋子，經過環保杯使用折讓{}元後，總共是{}元。".format(cup,drink_print,int(total_2/2),total_3,Total))