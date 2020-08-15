import pandas as pd

def main_info():
	main=["大麥克","雙層牛肉吉士堡","安格斯黑牛堡","嫩煎雞腿堡","麥香雞","麥克雞塊(6塊)","麥克雞塊(10塊)",
		  "勁辣雞腿堡","麥脆雞腿(2塊)","麥脆雞翅(2塊)","黃金起司豬排堡","麥香魚","千島黃金蝦堡"]
	number=list(range(1,14))
	main_price=[72,62,99,82,49,59,99,72,110,90,52,49,69]
	return main,number,main_price

def combo_info():
	Key=["A","B","C","D"]
	combo_price=[50,50,65,68]
	content=["中薯+33元飲料","沙拉+33元飲料","中薯+冰炫風","麥香(勁辣)雞腿+33元飲料"]
	return Key,combo_price,content


def ask_main():
	main,number,main_price=main_info()
	Main=pd.Series(main_price,index=number)
	for i in range(13):
		print("{}號:{}({}元)".format(number[i],main[i],main_price[i]))

	K=input("請問你要吃什麼？")
	while (K.isdigit() and not(int(K) in number)) or not(K.isdigit()):
		K=input("輸入錯誤！請重新輸入\n請問你要吃什麼？(請輸入整數)")
	return Main[int(K)],main[number.index(int(K))]

def ask_combo():
	Key,combo_price,content=combo_info()
	for i in range(len(Key)):
		print("{}套餐:{}({}元)".format(Key[i],combo_price[i],content[i]))
	combo=pd.Series(combo_price,index=Key)
	
	K=input("請問你要選搭配哪一個套餐?")
	
	while not(K in Key):
		K=input("輸入錯誤！請重新輸入\n請問你要選搭配哪一個套餐？(請輸入大寫字母)")
	return combo[K],K

if __name__ == '__main__':
	mainprice,mainmeal=ask_main()
	comboprice,combomeal=ask_combo()
	print("你的{}{}餐已經準備好了！總共是{}元!".format(mainmeal,combomeal,mainprice+comboprice))