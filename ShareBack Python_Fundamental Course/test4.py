print("M1")
i=0
num_list = [1, 2, 3]
for num in num_list:
    print(num)
    print("i={}".format(i))
    i+=1
    num_list.remove(num)
print(num_list)

print("\nM2")
num_list = [1, 2, 3]
i=0
for num in num_list[:]:
    print(num)
    print("i={}".format(i))
    i+=1
    num_list.remove(num)
print(num_list)
