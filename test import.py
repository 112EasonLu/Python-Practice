from pandas import Series as series
main=["大麥克","雙層牛肉吉士堡","安格斯黑牛堡","嫩煎雞腿堡","麥香雞","麥克雞塊(6塊)","麥克雞塊(10塊)",
		  "勁辣雞腿堡","麥脆雞腿(2塊)","麥脆雞翅(2塊)","黃金起司豬排堡","麥香魚","千島黃金蝦堡"]
main_price=[72,62,99,82,49,59,99,72,110,90,52,49,69]

Main=series(main_price,index=main)
print(Main)
#for i in range(13):
#	print(Main)