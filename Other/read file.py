import pandas as pd
import numpy as np

st = pd.Series([1,3,2,4], index=['a','B','c','D'])
print(type(st))
print(st)
print(st['c'])
print(st[2])
st_df = st.to_frame()
print(st_df)

f = [1,2,3,4,5,6,7,8,9]
sr_2 = pd.Series(f, pd.date_range(start='2018-05-01', end='2018-05-9'))
#pd.date_range是內建的日期序列產生器
print(sr_2)
print(sr_2 > 3)
#以Series的方式 輸出 True or False
print(sr_2[sr_2 > 3])

scores = [{"姓名":"小華","數學":90, "國文":80},
          {"姓名":"小明","數學":70, "國文":55},
          {"姓名":"小李","數學":45, "國文":75}]
score_df = pd.DataFrame(scores)
print(score_df)

scores2 = {"姓名":["小華","小明","小李"],
          "國文":[80,55,75],
          "數學":[90,70,45]}
score2_df = pd.DataFrame.from_dict(scores2)
print(score2_df) 

小華 = {'數學':90, '國文':80}
小明 = {'數學':70, '國文':55}
小李 = {'數學':45, '國文':75}
df = pd.DataFrame.from_dict([小華,小明,小李])
print(df)