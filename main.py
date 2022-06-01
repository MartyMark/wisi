import matplotlib
import mip as mip
import numpy as np

matplotlib.use('TkAgg')


class City:
    def __init__(self, x_coordinate, y_coordinate):
        self.x = x_coordinate
        self.y = y_coordinate


def generate_cities():
    cities_temp = []

    city_count = np.random.randint(low=10, high=15)

    for n in range(city_count):
        x = round(np.random.uniform(low=0.0, high=1.0), 2)
        y = round(np.random.uniform(low=0.0, high=1.0), 2)

        cities_temp.append(City(x, y))

    return cities_temp


def calculate_distance(cities_list):

    cities_distance = []

    for i in range(len(cities_list) - 1):

        city_distance = []

        for j in range(len(cities_list) - 1):

            if i == j:
                city_distance.append(0)
            else:
                distance = ((cities_list[i].x - cities_list[j].x) ** 2 + (
                            cities_list[i].y - cities_list[j].y) ** 2) ** 0.5
                city_distance.append(round(distance, 2))

        cities_distance.append(city_distance)

    return np.matrix(cities_distance)


cities = generate_cities()
distance_matrix = calculate_distance(cities)

print(distance_matrix)

m = mip.Model()

"""A = np.matrix([
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
"""
