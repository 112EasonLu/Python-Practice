inp=input('number:')
length=len(inp)
num=int(inp)
for i in range(1,length+1,2):
	A+=ROUND(num/(10*i))
	B+=ROUND(num/(10*(i+1))
#if num%2 ==0:
#	for i in range(1,length+1,2):
##		B+=ROUND(num/(10*(i+1))
#else:
#	for i in range(1,length+1,2):
#		A+=ROUND(num/(10*i))
#		B+=ROUND(num/(10*(i+1))		
#print(B)
#print(abs(B-A))