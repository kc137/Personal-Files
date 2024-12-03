# Knapsack Problem with Simulated Annealing

This code was implemented for the assignment on Heuristic Methods Course - Master in Applied Informatics.

## Tasks
1. The first task involves creating a program (parser) that is capable of reading various instances of problems. If a known collection of benchmark problems is not used, then the program must also include a random instance generator, from which random instances will be read by the **parser**. The use of known collections of benchmark problems is also allowed for the various problem categories.

2. The second task involves solving the corresponding problems using a methodology that includes a construction heuristic and an improvement heuristic. The construction heuristic will be used to create **initial solutions**, while the improvement heuristic will be used to **refine** these solutions by applying a set of local search techniques.

Overall, the solution for these programming assignments will require a good understanding of programming concepts such as file handling, data structures, and algorithm design. Additionally, a solid understanding of problem-solving techniques such as heuristic search algorithms and optimization methods will also be necessary.

## About
The aim of this project is to implement and apply the Simulated Annealing algorithm to solve the Knapsack problem.

### Selecting variables
Based on various tests, the algorithm was adapted to its current form. It was observed that, for the given example with a temperature of To=1000 and alpha=0.7, there was a profit improvement for temperature values ranging between 200 and 100. As a result, we conducted experimental modifications by changing the values of To to 200 and alpha to 0.999. This was done in order to observe the effects of small temperature reduction rates on the algorithm's performance.
