import numpy as np

def blockshaped(arr, cut_position):
	# matrix block
	# using numpy hsplit(col wise) and vsplit (row wise)
	#cut_position is sliceing-site

	block=np.vsplit(arr,[cut_position])

	upper_half = np.hsplit(block[0], [cut_position,len(arr)])
	lower_half = np.hsplit(block[1], [cut_position,len(arr)])

	upper_left = upper_half[0]
	upper_right = upper_half[1]
	lower_left = lower_half[0]
	lower_right = lower_half[1]

	return 	upper_left,upper_right,lower_left,lower_right 


K=[[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]]

k1=[[0.333,0,-0.333,0,0,0],[0,0,0,0,0,0],[-0.333,0,0.333,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]]
k2=[[0.072,0.096,0,0,-0.072,-0.096],[0.096,0.128,0,0,-0.096,-0.128],[0,0,0,0,0,0],[0,0,0,0,0,0],[-0.072,-0.096,0,0,0.072,0.096],[-0.096,-0.128,0,0,0.096,0.128]]
for i in range(6):
	for j in range(6):
		K[i][j]=(k1[i][j]+k2[i][j])


K=np.array(K)

		
upper_left,upper_right,lower_left,lower_right=blockshaped(K, 2)
print(upper_left,'\n')
print(upper_right,'\n')
print(lower_left,'\n')
print(lower_right,'\n')