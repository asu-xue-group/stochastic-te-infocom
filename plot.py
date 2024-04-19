import matplotlib.pyplot as plt
import numpy as np

xpoints = np.array([0.85, 0.9, 0.95, 1])
# ypoints = np.array([81.16, 72.14, 51.23, 37.88])
ypoints = np.array([80.45, 73.4, 57.07, 42.38])

plt.plot(xpoints, ypoints, marker = 'o')

plt.xlabel("Confidence Level")
plt.ylabel("Upper Bound of Gap")
plt.show()