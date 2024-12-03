# %matplotlib inline
# import matplotlib, numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt, numpy as np

x = np.arange(0, 150, 5)
y1 = 100 - 2*x
y2 = 80 - x
y3 = 72 - 4.7*x

plt.plot(x, y1, label = "2x + y <= 100")
plt.plot(x, y2, label = "x + y <= 80")
plt.plot(x, y3, label = "4.7x + y <= 72")

# xf, yf = [], []
# 
# for xi in x:
#     for yi in np.arange(0, 100.5, 0.5):
#         if (2*xi + yi <= 100) and (xi + yi <= 80) and (4.7*xi + yi <= 72):
#             xf.append(xi)
#             yf.append(yi)
# plt.fill_between(xf, yf, alpha = 1)
# plt.fill_between(x, y2)


plt.xlim(0, 70)
plt.ylim(0, 100)
plt.show()