
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#import FontProperties 

# find start point
inputfile = open('/Users/luyisheng/Downloads/hrxpsfiles/H-4-dp.csv')

lookup = 'O1s'
start_row = 0

for num, line in enumerate(inputfile, 1):
    if lookup in line:
        start_row = num + 1
        print ('found at line:', num)
        print (start_row)

# process file
inputfile2 = open('/Users/luyisheng/Downloads/hrxpsfiles/H-4-dp.csv')

df = pd.DataFrame()

df = pd.read_csv(inputfile2, sep='\t', skiprows=start_row, dtype=str, header=None, names=[' ','1','2','3','4','5','6','7','8','9','10','11','12'])
df = df.loc[:,[' ','1','2','3','4','5','6','7','8','9','10','11','12']]

df = df.set_index(' ')
#drop last row 'EXPERIMENTABORTED	TOGGLE	T	Experiment Aborted'
df.drop(df.tail(1).index,inplace=True) 
#df= df.dropna(subset=['1','2','3','4','5','6','7','8','9','10','11','12'])

df.Vf=pd.to_numeric(df.'1')
df.Im=pd.to_numeric(df.'2')
df.Vf=pd.to_numeric(df.'3')
df.Im=pd.to_numeric(df.'4')
df.Vf=pd.to_numeric(df.'5')
df.Im=pd.to_numeric(df.'6')
df.Im=abs(df.Im)
df.to_csv('/Users/luyisheng/Downloads/hrxpsfiles/H-4-dp-2.csv', index = False)

#df.plot(x='Im',y='Vf',logx=True,kind='line')'font.serif':'Times New Roman'
#plt.show()


#df.plot.line()

# In[ ]: