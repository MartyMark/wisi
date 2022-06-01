import matplotlib
import numpy as np
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')

A = np.matrix([
    [1, 0, 0, 0],
    [1, 1, 1, 1],
    [1, 2, 4, 8],
    [1, 4, 16, 64]
])

b = np.array([-3, 1, 2, 7])
a = np.linalg.solve(A, b)

print(a)

tx = np.linspace(0, 5, 200)
fx = a[0] + a[1] * tx + a[2] * tx ** 2 + a[3] * tx ** 3

plt.plot(tx, fx, 'r')
plt.plot([0, 1, 2, 4], [-3, 1, 2, 7], 'o', 2)
plt.ylabel('x')
# plt.xlim([0,1])
# plt.ylim([0,0.13])
plt.ylabel('y')
plt.title('Interpolation')
plt.show()
