a,b,c=input('three side of triangle a b c').split()
S=[int(a),int(b),int(c)]
S.sort()
A=S[0]
B=S[1]
C=S[2]
indenti=A**2+B**2

if A+B <= C :
	print('No')
else:
	if indenti == C**2:
		print(A,B,C,'\nRight triangle')
	elif indenti > C**2:
		print(A,B,C,'\nAcute triangle')
	else:
		print(A,B,C,'\nObtuse triangle')