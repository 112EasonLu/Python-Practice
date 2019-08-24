#a=int(input("Give a nature num:"))

#if a>0 :
#	a+=((a**(1/2)+20)%2 *13)//2.3
#	print("Your lucky num is %d" %(a))
#else:
#	print("Your input is not acceptable")

time=int(input("Time:"))
if time >= 10 and time <30:
	print("A")
elif time >= 30 and time <60:
	print("B")
elif time >= 60 and time <120:
	print("C")
elif time >= 120:
	print("D")
else:
	print("You're GG!!!!!")
