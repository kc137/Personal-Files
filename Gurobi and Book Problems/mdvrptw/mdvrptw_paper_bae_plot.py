import matplotlib.pyplot as plt, matplotlib, random
matplotlib.use("tkagg")
from data import coords as xy_coords

edges = {1: [(3, 27),
  (6, 37),
  (9, 42),
  (10, 11),
  (11, 45),
  (27, 48),
  (37, 9),
  (39, 50),
  (42, 46),
  (43, 39),
  (45, 6),
  (46, 43),
  (48, 10),
  (50, 3)],
 2: [(7, 41),
  (22, 7),
  (31, 44),
  (32, 35),
  (34, 50),
  (35, 34),
  (36, 31),
  (41, 36),
  (44, 32),
  (50, 22)],
 3: [(1, 14),
  (4, 19),
  (5, 8),
  (8, 13),
  (13, 33),
  (14, 51),
  (16, 29),
  (19, 1),
  (20, 28),
  (28, 4),
  (29, 5),
  (33, 20),
  (51, 16)],
 4: [(2, 52),
  (12, 21),
  (15, 25),
  (17, 40),
  (18, 17),
  (21, 24),
  (23, 26),
  (24, 2),
  (25, 23),
  (26, 18),
  (30, 15),
  (38, 12),
  (40, 38),
  (47, 30),
  (52, 47)]}

colors_list = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
             for i in range(len(edges))]
colors = {1 : colors_list[0], 
          2 : colors_list[0], 
          3 : colors_list[1], 
          4 : colors_list[2]}

for v in edges:
    for p1, p2 in edges[v]:
        pts = [xy_coords[p1-1], xy_coords[p2-1]]
        print(pts)
        plt.scatter(pts[0][0], pts[0][1], c = colors[v])
        plt.scatter(pts[1][0], pts[1][1], c = colors[v])
        plt.plot(*zip(*pts), c = colors[v])