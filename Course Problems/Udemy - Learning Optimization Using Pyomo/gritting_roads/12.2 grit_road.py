# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 14:27:35 2023

@author: ayan
"""

from pyomo.environ import *

model = AbstractModel("Gritting Roads")

model.intersections = Set()

model.arcs = Set(within=model.intersections * model.intersections)
model.lengths = Param(model.arcs,within=NonNegativeIntegers)

model.x = Var(model.arcs,within=NonNegativeIntegers)

def obj(model):
    return sum(model.lengths[i,j] * model.x[i,j] for (i,j) in model.arcs)
model.min_path = Objective(rule=obj)

def flow_conservation(model,k):
    return sum(model.x[j,i] for (j,i) in model.arcs if i == k) == sum(model.x[i,j] for (i,j) in model.arcs if i == k)
model.arcs_conserv = Constraint(model.intersections,rule=flow_conservation)

def each_street_pass(model,i,j):
    return model.x[i,j] >= 1
model.Constraint2 = Constraint(model.arcs,rule=each_street_pass)

solver = SolverFactory("cbc")
instance = model.create_instance("12.1 grit_road.dat")
results = solver.solve(instance)

for (i,j) in instance.arcs:
    if value(instance.x[i,j]) == 1:
        print(f'Street {(i,j)} is passed once')
    elif value(instance.x[i,j]) > 1:
        print(f'Street {(i,j)} is passed {value(instance.x[i,j])} times')
print(f'The minimum length of the entire path is {value(instance.min_path)}')

