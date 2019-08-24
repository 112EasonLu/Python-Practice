# I'am 
# 有區分大小寫，數字不可以再英文前
# notice that "1name" is not acceptable because head of num.
# 駝峰命名法： evenOne evenTwo evenTree
# 底線命名法： even_one even_two even_three
# "=" is "assignment operator"

#part 1
Name1=input("What is your name1?")
Name2=input("What is your name2?")
print("Hello,",Name1+".")
print("Hello, "+Name1+".")
print("Hello, %s." %Name1)
print("Hello, %s, %s." %(Name1,Name2))
#以下不能work
#print("Hello, %s, %s.",%(Name1,Name2))
#print("Hello, %s, %s." %Name1, %Name2)


#part 2
num=input("What is your lucky num?")
# Don't forget input is str.
# num=int(input("What is your lucky num?")) exact policy.
print("Your lucky num is %d." %(int(num)))


#%()這是函數嗎？