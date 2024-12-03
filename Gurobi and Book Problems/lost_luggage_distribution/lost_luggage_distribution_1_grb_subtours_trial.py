tuples = [(0, 5), (0, 16), (1, 0), (2, 10), (3, 4), (4, 0), (5, 7), (6, 2), 
          (7, 9), (8, 1), (9, 13), (10, 11), (11, 8), (12, 14), (13, 12), 
          (14, 15), (15, 3), (16, 6)]

tuples = [
 ( 0  , 5  )
 ,( 0  , 13 )
 ,( 1  , 8  )
 ,( 2  , 10 )
 ,( 3  , 4  )
 ,( 4  , 0  )
 ,( 5  , 16 )
 ,( 6  , 12 )
 ,( 7  , 9  )
 ,( 8  , 11 )
 ,( 9  , 0  )
 ,( 10 , 1  )
 ,( 11 , 2  )
 ,( 12 , 14 )
 ,( 13 , 7  )
 ,( 14 , 15 )
 ,( 15 , 3  )
 ,( 16 , 6  )
 ]

tuples = [(1, 2), (1, 7), (1, 10), (1, 13), (1, 15), (2, 12), (3, 5), (4, 1), (5, 3), (6, 1), (7, 8), (8, 16), (9, 1), (10, 11), (11, 1), (12, 4), (13, 1), (14, 17), (15, 14), (16, 9), (17, 6)]
tuples = [(tup[0] - 1, tup[1] - 1) for tup in tuples]

"""
 ( 0  , 5  )
 ( 0  , 13 )
 ( 1  , 8  )
 ( 2  , 10 )
 ( 3  , 4  )
 ( 4  , 0  )
 ( 5  , 16 )
 ( 6  , 12 )
 ( 7  , 9  )
 ( 8  , 11 )
 ( 9  , 0  )
 ( 10 , 1  )
 ( 11 , 2  )
 ( 12 , 14 )
 ( 13 , 7  )
 ( 14 , 15 )
 ( 15 , 3  )
 ( 16 , 6  )
>
[1, 8, 11, 2, 10]
"""

start_tuples = [(0, 5), (0, 16)]
N = len(tuples)

def get_subtours(edges):
    total_origin = sum([1 for (i, j) in edges if i == 0])
    unvisited = [total_origin] + [1 for _ in range(16)]
    left = len(edges)
    subtours = []
    
    while left > 0:
        subtour = []
        subtours.append(subtour)
        for i in range(N-1):
            if unvisited[i]:
                start = i
                break
        
        while True:
            subtour.append(start)
            if unvisited[start]:
                unvisited[start] -= 1
                left -= 1
            
            next_node = next((j for (i, j) in edges if i == start and unvisited[j]), None) # and edges[i, j] >= 0.9
            
            if not next_node or not unvisited[next_node]:
                break
            
            start = next_node
    return subtours
    # print(subtours)
    # print(unvisited)
    # remaining = []
    # for i in range(len(unvisited)):
    #     if unvisited[i]:
    #         remaining.append(i+1)
    # return remaining

print(get_subtours(tuples))