"""
Created on Sat Jan  8 15:02:47 2022

@author: aggelos
"""

from knapsack.generator import generateData
from knapsack.parser import parseData
from knapsack.knapsack import Knapsack

if __name__ == "__main__":
    print('Genarate random data')
    #if you uncomment data will be randomly generated
    #generateData()
    print('Parsing data')
    capacity,weights,profits = parseData()
    
    print('capacity',capacity)
    print()
    print('weights',weights)
    print()
    print('profits',profits)
    print()
    
    print('Calclulate knapsack')

    k = Knapsack(capacity, weights, profits)
    k.greedy()
    k.simulatedAnnealing() # Solve using the simulated annealing algorithm
