import numpy as np
list_1=[[[1,2,3],[4,5,6],[7,8,9]],
		[[11,12,13],[14,15,16],[17,18,19]]]

list_2=[[[1,2,3],[4,5,6]],
		[[7,8,9],[10,11,12]],
		[[13,14,15],[16,17,18]]]

print(list_1)
print(list_2)
print("list_1: shape is {}".format(np.shape(list_1)))
print("list_2: shape is {}".format(np.shape(list_2)))
print(list_2[1][1][0])# =10

#1-D(elements)
#2-D(rows,elements)
#3-D(layers,rows,elements)