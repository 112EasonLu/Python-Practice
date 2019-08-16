students = [
        ['john', 'A', 15],
        ['jane', 'B', 12],
        ['dave', 'C', 8],
        ['ryan', 'B', 10],
]

# 證明你是對的
print(students[0]) #-> ['john', 'A', 15],
print(students[0][1]) #-> A

# 用 lambda 排序概念很像是這樣
    print(students[i]) # 可以知道各個element 代表的值

# 若用第一個排序，他的 x 相當一element或者說裡面第幾個東西，有點像是index的感覺，：後面是比較標準
student_sort = sorted(students, key = lambda x : x[2])
print('student_sort : ', student_sort)


s = [2, 3, 1, 4, 9]
for i in range(len(s)):
    print(s[i]) # 可以知道各個element 代表的值

# 若用第二個排序，他的 k 相當一element或者說裡面第幾個東西，有點像是index的感覺，：後面是比較標準
sorted_s = sorted(range(len(s)), key = lambda k : s[k]) 

#Range(len(s))是在創造一個s的index list
#Range(len(s))=[0,1,2,3,4,......]

print('sorted_s : ', sorted_s)


#用linked list 角度來講，你每個lambda變數(x or k)都是一個指標，他有 1~list 長度個，它會指向 : s[k]/ x[2]，那最後你會用 : 後方來排序，那結果會以你的指標來展現


# 以第二個範例做個總結：

# In short,lambda k 的 k 是指前面第一個引數range(len(s))裡面的元素， 而 lambda 可以想成依序抓出每一個k，

# 將 k assign 一個東西 s[k] (就是冒號後面的東西)，形成有點像是linked list(k和s[k]兩兩一組)，

# 然後我們會用s[k]作為用來比較的東西，利用s[k]的大小進行排列，因為k和s[k]兩兩一組，連體嬰要移動就要一起動！

# 最後排完後k的順序就是我們要的index sort

# Reference https://my.oschina.net/u/2264246/blog/654825