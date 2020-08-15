
import time
# Method 1 - Dynamic Programming
def DP_Fibonacci(n):
	F=[1]*2
	i=2
	while i <=n:
		F.append(F[i-1]+F[i-2])
		i+=1
	return F[n]

# Method 2 - Recursion
def Re_Fibonacci(N):     
    if N>1:
    	return Re_Fibonacci(N-1)+Re_Fibonacci(N-2)
    else: 
    	return 1

print("Fibonacci(n), n=")
n=int(input())
tStart1 = time.time()
print("Fibonacci({})={}".format(n,DP_Fibonacci(n)))
tEND1 = time.time()
tStart2 = time.time()
print("Fibonacci({})={}".format(n,Re_Fibonacci(n)))
tEND2 = time.time()
print("Dynamic Programming:{} sec".format(tEND1-tStart1))
print("Recursion:{} sec".format(tEND2-tStart2))
