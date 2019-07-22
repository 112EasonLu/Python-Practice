import numpy as np
import matplotlib.pyplot as plt
#def activation (self, x):

#	return 1/(1+np.exp(-x))
def ReLu(x):
	return max(0.0,x)

def Datas(a,b):
	xx=[i*(-1) for i in a]
	xxx=[i*(-1) for i in b]
	y1=1/(1+np.exp(xx))
	y2=1/(1+np.exp(xxx))
	return y1,y2

def plot(x,ret,m,n,col):

	return plt.subplot(m, 1, n),plt.plot(x,ret,color = col)


#if __nane__=="__main__":
x=[[i for i in range(-5,20)],[i for i in range(-10,10)]]
#y1=[1/(1+np.exp(-j)) for j in range(-10,10)]
#y1=[ReLu(k) for k in range(-5,20)]
#y2=[ReLu(k) for k in range(-10,10)]
y=Datas(x[0],x[1])
fig = plt.figure(figsize=(6, 6), dpi=80)
plot(x[0],y[0],2,1,'red'),plot(x[1],y[1],2,2,'blue')
plt.show()