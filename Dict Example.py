#!/usr/bin/python
# -*- coding: utf-8 -*-

data = {'id' : 1, 'name' : 'tom'}
print(type(data)) # <type 'list'>
print(len(data)) # 2

print(data)
print(data['id'])
print(data['name'])

# -------------------------------
data2 = {'id' : [], 'name' : []}
data2['id'].append(1)
data2['name'].append('jack')
data2['id'].append(2)
data2['name'].append('andy')
data2['id'].append(3)
data2['name'].append('ma rk')
print(data2)
