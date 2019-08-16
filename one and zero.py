def binary_array_to_number(arr):
    ans=0
    leng=len(arr)
    for i in range(leng):
        ans=ans+arr[i]*(2**(leng-i-1))
    return ans
if __name__ == "__main__":
	print(binary_array_to_number([0,0,0,1]))