a=input("i= ")
b=input("j= ")
I=min(int(a),int(b))
J=max(int(a),int(b))
mx=0
for i in range(I,J+1):
	count=1
	while i!=1:
		if i%2 != 0:
			i=3*i+1
		else :
			i=i/2 
		count+=1
		if count>mx:
			mx=count
print(a,b,mx)