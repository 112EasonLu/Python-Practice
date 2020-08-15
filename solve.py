import numpy as np
# Method 1
A=np.array([
	[1,2,3,4,5,6,7,8],
	[1,1,7,9,4,4,1,6],
	[4,0,0,1,9,4,8,7],
	[5,9,4,1,1,2,8,7],
	[5,2,0,1,3,1,4,6],
	[0,7,5,2,5,2,0,0],
	[7,5,0,4,0,0,2,1],
	[0,6,5,2,5,0,1,9]
	])

y=np.array([105,987,533,945,888,569,117,112]).reshape(8, 1)

A_inv = np.linalg.inv(A)
ans = A_inv.dot(y)

B=A.dot(ans)
print (ans)
print (B)