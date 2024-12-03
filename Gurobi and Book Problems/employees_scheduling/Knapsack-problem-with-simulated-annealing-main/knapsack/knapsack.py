# -*- coding: utf-8 -*-
"""
Created on Sat Jan  8 15:02:47 2022

@author: aggelos
"""
class Knapsack:
    def __init__(self, capacity, weights, profits):
        self.capacity = capacity
        self.weights = weights
        self.profits = profits
        self.solution =[]
        
    # generate output as a binary string related to the possition
    def calculateOutput(self,itemDict):
        self.solution=[]
        for i in range(len(itemDict)):
            self.solution.append(itemDict[i][3])
        pass
    
    def greedy(self):
        # itemsList = [[p, w, p//w,'0'] for p,w in zip(profits,weights)]
        itemDict = { 
            i:item for i,item in enumerate(
                    [p, w, p/w,0] for p,w in zip(self.profits,self.weights)
                ) 
        }
        # itemsList = sorted(itemsList, key=lambda x: x[2],reverse=True)
        #for i in sorted(itemDict.items(), key=lambda item: item[1][2],reverse=True):
        #    print(itemDict[i[0]])
              
        c = self.capacity
        total_profit=0
        total_weight=0
        for i in sorted(itemDict.items(), key=lambda item: item[1][2],reverse=True):
            if c>0:
                if c-i[1][1]>=0:
                    c-=i[1][1]
                    itemDict[i[0]][3]=1
                    total_profit+=itemDict[i[0]][0]
                    total_weight+=itemDict[i[0]][1]
            else:
                break
        # print values with 3rd cell 1 (taken in sack)
    #    for i in range(len(itemDict)):
    #        if itemDict[i][3]=='1':
    #            print(itemDict[i])
    
        
        self.calculateOutput(itemDict)
        print(''.join([str(i) for i in self.solution]))
        print('total profit',total_profit)
        print('total weight',total_weight)
        #print('total items',bestX.count(1))
        
        #MAYBE THINK OF A WHILE SOLUTION 
     #   while(c>0):
     #       if (c>=item[i]):
     #           c-=item[1]
    #            item[2]='1'
    #        else:
    #            item++
                
        #print('\n'.join([str(item) for i,item in itemDict]))
        #for item in itemDict.items():
        #    print(item)
    def indexXSumOfY(self,array1,array2):
        sumY=0
        for i in range(len(array1)):
            if array1[i]==1:
                sumY+=array2[i]
        return sumY

    def P(self,array):
        return self.indexXSumOfY(array,self.profits)
    
    def W(self,array):
        return self.indexXSumOfY(array,self.weights)
    
    
    #Simulated Annealing method
    def simulatedAnnealing(self):
        from math import exp
        import random
        from datetime import datetime as dt
        # set time as seed
        random.seed(3)
        
        
        alpha=0.99999999
        

        cmax=1000          # number of loops

        
        t_o=200
        c=0
        t=t_o
        x=self.solution.copy()
        bestX=x.copy()
        tempChange=cmax
        print('x\t',
              '\tprofit',self.P(x),
              '\tweight',self.W(x),
              '\titems\t',x.count(1),
              ''.join([str(i) for i in x])
        )
        for c in range(cmax):
            y=x.copy()
            j=random.randint(0,len(self.profits)-1)
            # FLIP RANDOM INDEX (ITEM) for neighbouhood solution
            y[j]=1-y[j]
            '''
            print(y)
            print(x)
            print(self.P(y))
            print(self.P(x))
            print(self.W(y))
            print(self.W(x))
            print(y.count(1))
            print(x.count(1))
            '''

            #delta = self.P(y)-self.P(x)
            delta = self.P(y)-self.P(x)
            
            
            if(self.W(y)<=self.capacity):
                u=random.uniform(0.0,1.0)
                if(delta>0 or exp(-abs(delta)/t)>u):
                    x=y.copy()
                    tempChange-=1
                    if tempChange%10==0:
                        t=alpha*t
                        print('change of T to',t)
                    print('y\t',
                      '\tprofit',self.P(y),
                      '\tweight',self.W(y),
                      '\titems\t',y.count(1),
                      ''.join([str(i) for i in y])
                    )
                    if self.P(x)>=self.P(bestX):
                        bestX=x.copy()
                
                # if I changed 5 times the x then reduce temperature
        print('\nbestX',
              '\tprofit',self.P(bestX),
              '\tweight',self.W(bestX),
              '\titems',bestX.count(1),
              ''.join([str(i) for i in bestX])
        )
            
        #print('bestX')
        self.solution=bestX
        #print(''.join([str(i) for i in self.solution]))
        #print('total profit',self.P(self.solution))
        #print('total weight',self.W(self.solution))
        #print('total items',self.solution.count(1))
        pass