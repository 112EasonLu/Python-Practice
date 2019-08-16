#演算法 找質數
class prime:
#	def __init__(self,n):
#		self.n=n
	def eratosthenes(self,n):
#		n=self.n
		isPrime = [True]*(n+1)
		isPrime[1] = False
		for i in range(2, int(n** 0.5) + 1):
			if  isPrime[i]: # if isPrime[i] is True, thast is, i is prime value
				for j in range(i*i, n+1, i): # 如果i是質數，則篩掉它的倍數
					isPrime[j] = False
		return [x for x in range(2,n+1) if isPrime[x]]

#if __name__ == "__main__":
#	print(eratosthenes(120))
print(prime().eratosthenes(100))
