import numpy as np
import matplotlib.pyplot as plt
class maze:
	def slove(sele,mp):
		t_x=len(mp)
		t_y=len(mp[0])
		start = [1, 0]
		end = [99, 100]
		i,j=start[0],start[1]
		ei,ej=end[0],end[1]
		step=[[0,1],[0,-1],[1,0],[-1,0]]

		# 設一個陣列，用來標記走過的座標
		book = []
		for m in range(t_x):
			book.append([0] * t_y)
		father=[0] * t_x * t_y
		pas=[0] * t_x * t_y
		stack = [(i, j)]
		tail=1
		flag = 0
		head=0
		while stack:
			for k in range(4):
				i= stack[head][0]+step[k][0]
				j= stack[head][1]+step[k][1]
				if (i,j) == (ei,ej) :
					flag = 1
					break
				if mp[i][j]==0 :
					if (book[i][j]== 0) :
						book[i][j]= 1
						father[tail]=head
						pas[tail]=father[head]+1
						tail += 1
						stack.append((i, j))
						#print(stack[:])
			head += 1
			if flag == 1:
				break
			
			
		print(father[:])
		print(head)
		while pas[-1]==0:
			pas.pop()
#		print(pas[:])
#		print(pas[:])
#		ans=mp.copy()
#		for u in range(len(stack)):
#			x, y = stack[u][0],stack[u][1]
#			ans[x][y] = 1
#			print(stack[u])
		return pas


data = np.load('/Users/luyisheng/Downloads/quizzes/maze_data.npy')
index = np.random.randint(50)
ret =maze().slove(data[index])
fig = plt.figure(figsize=(6, 6), dpi=80)
plt.imshow(ret, cmap='Blues')
plt.show()
