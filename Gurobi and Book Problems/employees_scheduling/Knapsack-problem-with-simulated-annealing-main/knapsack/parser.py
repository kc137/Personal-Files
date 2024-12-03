# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 19:05:04 2021

@author: aggelos

"""


#capacity = 0
#weights = []    # weights of items
#profits = []    # profits of items

def parseData():
    capacity = 0
    weights = []    # weights of items
    profits = []    # profits of items
    f = open("dataset.txt", "r")
    
    lines = f.readlines()
    
    flag = False
    for i in range(len(lines)):
        if "capacity" in lines[i]:
            capacity = int(lines[i+1].strip())
        if flag:
            x,y=lines[i].strip().split()
            weights.append(int(x))
            profits.append(int(y))
        if "weights profits" in lines[i]:
            flag=True
        pass
    f.close()
    return capacity,weights,profits

#capacity,weights,profits=parseData()
#print("capacity",capacity)
#print("weights" , weights)
#print("profits" , profits)