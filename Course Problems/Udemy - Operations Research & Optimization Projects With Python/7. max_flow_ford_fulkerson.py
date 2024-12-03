from collections import defaultdict

class Graph:
    
    def __init__(self, graph):
        self.graph = graph
        self.row = len(graph)
    
    # BFS for finding the path
    def bfs(self, s, t, parent):
        print(parent)
        visits = [False]*self.row
        q = []
        q.append(s)
        visits[s] = True
        
        while q:
            u = q.pop(0)
            
            for idx, val in enumerate(self.graph[u]):
                if visits[idx] == False and val:
                    q.append(idx)
                    visits[idx] = True
                    parent[idx] = u
        return True if visits[t] else False

    # Now to the main Ford-Fulkerson Algorithm
    def ford_fulkerson_algo(self, source, sink):
        parent = [-1]*self.row
        max_flow = 0
        
        while self.bfs(source, sink, parent):
            # print(parent)
            path_flow = float("inf")
            s = sink
            while s != source:
                path_flow = min(path_flow, self.graph[parent[s]][s])
                s = parent[s]
            
            max_flow += path_flow
            
            # Now updating the residual values of edges
            v = sink
            while v != source:
                u = parent[v]
                self.graph[u][v] -= path_flow
                self.graph[v][u] += path_flow
                v = parent[v]
        return max_flow
    
# graph = [[0, 8, 0, 0, 3, 0],
#          [0, 0, 9, 0, 0, 0],
#          [0, 0, 0, 0, 7, 2],
#          [0, 0, 0, 0, 0, 5],
#          [0, 0, 7, 4, 0, 0],
#          [0, 0, 0, 0, 0, 0]]

graph = [[0, 16, 13, 0, 0, 0],
        [0, 0, 10, 12, 0, 0],
        [0, 4, 0, 0, 14, 0],
        [0, 0, 9, 0, 0, 20],
        [0, 0, 0, 7, 0, 4],
        [0, 0, 0, 0, 0, 0]]

graph_obj= Graph(graph)

source, sink = 0, 5
print(f"Max-Flow by Ford-Fulkerson Algorithm : {graph_obj.ford_fulkerson_algo(source, sink)}")