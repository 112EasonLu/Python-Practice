
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#import FontProperties 

# find start point
inputfile = open('/Users/luyisheng/Desktop/HEA-0712-01MHS-1.DTA')

lookup = '	#	s	V vs. Ref.	A	V	V	V	#	bits'
start_row = 0

for num, line in enumerate(inputfile, 1):
    if lookup in line:
        start_row = num + 1
        print ('found at line:', num)
        print (start_row)

# process file
inputfile2 = open('/Users/luyisheng/Desktop/HEA-0712-01MHS-1.DTA')

df = pd.DataFrame()

df = pd.read_csv(inputfile2, sep='\t', skiprows=start_row, dtype=str, header=None, names=['Pt','T','Vf','Im','Vu','Sig','Ach','IERange','Over'])
df = df.loc[:,['Pt','Vf','Im']]

df = df.set_index('Pt')
#drop last row 'EXPERIMENTABORTED	TOGGLE	T	Experiment Aborted'
df.drop(df.tail(1).index,inplace=True) 
#df= df.dropna(subset=['Vf','Im'])

df.Vf=pd.to_numeric(df.Vf)
df.Im=pd.to_numeric(df.Im)
df.Im=abs(df.Im)
df.to_csv('/Users/luyisheng/Desktop/HEA-0712-01MHS-1.csv', index = False)

#df.plot(x='Im',y='Vf',logx=True,kind='line')'font.serif':'Times New Roman'
#plt.show()


#df.plot.line()

# In[ ]:





# In[ ]:





# In[ ]:




