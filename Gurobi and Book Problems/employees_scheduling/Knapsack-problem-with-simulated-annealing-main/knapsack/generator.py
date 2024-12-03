# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 16:51:18 2021

@author: aggelos
"""

# seed the pseudorandom number generator
import random
from datetime import datetime as dt

# set time as seed
random.seed(3)

capacity = 0
n = 0           # number  of items
weights = []    # weights of items
profits = []    # profits of items

def generateInteger( min, max):
    return random.randint(min, max)

# create a list of integers of listSize items
# with Max possible value max and Min min
def generateListOfIntegers( min, max, listSize):
    return [generateInteger(min,max) for i in range(listSize)]
    
def writeFile(fileName,fileLines):
    f = open(fileName,'w')
    for line in fileLines:
        f.write(line)
    f.close()

def printLists(weights,profits,lines):
    print(list(zip(weights, profits)))
    #print lines
    print("".join(lines))

def generateData():
    # create an integer 
    n = 50 #for standar value of n, OR generateInteger(10,100) for random value of n 
        
    # list of n items max weight 50 and min 0
    weights = generateListOfIntegers(1,50,n)
    
    # list of n items max profit 999 and min 0
    profits = generateListOfIntegers(1,999,n)
    
    #set capacity
    capacity = 100 #for standar value of capacity, OR round(n/5) for a percentage of n
    #set list with each line to be written
    #lines = [
    #      "capacity\n"+str(capacity)+'\n'
    #    , "weights\n" +"\n".join([str(w) for w in weights])+'\n'
    #    , "profits\n" +"\n".join([str(p) for p in profits]) +'\n'
    #]
    
    # set lists to be printed as pairs
    lines = [
          "capacity\n"+str(capacity)+'\n'
        , "weights profits\n" +"\n".join([str(pair[0])+" "+str(pair[1]) for pair in zip(weights, profits)])
    ]
    writeFile('dataset.txt',lines)
    
    #printLists(weights,profits,lines)
    pass
