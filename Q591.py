from datetime import datetime, timedelta
f = open('/Users/luyisheng/Desktop/input.txt','r')
contents = f.readlines()
f.close()
new_contents = []

# Get rid of empty lines
for line in contents:
    # Strip whitespace, should leave nothing if empty line was just "\n"
	if not line.strip():
		continue
    # We got something, save it
	else:
		new_contents.append(line)

for i in range(0,len(new_contents)):
	new_contents[i] = new_contents[i].strip('\n')

print(new_contents)
#for line in f.readline():
#	print(line)

num=int(new_contents[0])


for i in range(1,num+1):
	D1=new_contents[2*i-1]
	D2=new_contents[2*i]
	datetime_object1 = datetime.strptime(D1, '%d/%m/%Y')
	datetime_object2 = datetime.strptime(D2, '%d/%m/%Y')
	print (int((datetime_object1-datetime_object2)/timedelta(days=365.2425)))