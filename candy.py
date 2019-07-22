def evaluation(a,b,c,d):
    print(d)
    if b==a and (b==c or b<c):
        return 1
    elif b==a and b>c:
        return 2
    elif b>a and (c>b or b>c):
        return d+1
    elif b>a and b==c:
        return d+1
    elif b<a and b==c:
        return 1
    elif b<a and b<c:
        return 1
    elif b<a and b>c:
        return 1
    else:
        return 1    
#[29,51,87,87,72,12]
class Solution:
    def candy(self, ratings: List[int]) -> int:
        M=[1,2,3,4,5,6]
        M.pop()
        need_val=0
        print(len(ratings))
        for i in range(len(ratings)):
            if len(ratings)==1:
                need=[1]
            elif i==0 :
                if ratings[1]> ratings[0]:
                    need=[1]
                else:
                    need=[2]             
            elif i==len(ratings)-1:
                if ratings[-1]> ratings[-2]:
                    need.append(need[-1]+1)
                else:
                    need.append(1)
            else:
              #  print('test,',evaluation(ratings[i-1],ratings[i],ratings[i+1],need[i-1]))
                need.append(evaluation(ratings[i-1],ratings[i],ratings[i+1],need[i-1]))
                
            need_val=need_val+need[i] 
            print(need)
        return need_val