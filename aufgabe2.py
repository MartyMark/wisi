import matplotlib
import mip as mip
import numpy as np
from itertools import product, combinations, tee
import matplotlib.pyplot as plt
from scipy.optimize import linprog
from scipy.sparse import csr_matrix
import copy


# matplotlib.use('TkAgg')


class City:
    def __init__(self, x_coordinate, y_coordinate, name):
        self.x = x_coordinate
        self.y = y_coordinate
        self.name = name


# Generiert statische Testdaten
def generate_test_cities():
    return [
        City(0.1, 0.1, 0),
        City(0.1, 0.6, 1),
        City(0.6, 0.2, 2),
        City(0.8, 0.9, 3)
    ]


# Generiert die Städte, die die x und y-Koordinate zwischen 0 und 1 beinhalten
def generate_cities():
    cities_temp = []

    city_count = np.random.randint(low=15, high=20)

    for n in range(city_count):
        x_coordinate = round(np.random.uniform(low=0.0, high=1.0), 2)
        y_coordinate = round(np.random.uniform(low=0.0, high=1.0), 2)

        cities_temp.append(City(x_coordinate, y_coordinate, n))

    return cities_temp


def calculate_distance():
    cities_distance = []
    for (i, j) in combinations(cities_range, 2):
        distance = ((cities[i].x - cities[j].x) ** 2 + (
                cities[i].y - cities[j].y) ** 2) ** 0.5
        print(distance)
        cities_distance.append(round(distance, 2))

    return cities_distance


def generate_aeq():
    aeq = []
    iter_idxs = tee(idxs, len(cities))
    for i in range(len(cities)):
        single_aeq = []
        for (k, j) in iter_idxs[i]:
            if i == k or i == j:
                single_aeq.append(1)
            else:
                single_aeq.append(0)
        aeq.append(single_aeq)
    return aeq


# Plottet alle vorhanden Städte:
def plot_cities():
    for i in range(len(cities)):
        plt.scatter(cities[i].x, cities[i].y, s=10)
        plt.annotate(i, (cities[i].x, cities[i].y))


# Plottet die herausgefunden Routen
def plot_routes(res_x):
    for index, el in enumerate(res_x):
        # print("Index:" , idx, "Value: ", x)
        if round(el) == 1:
            (c1, c2) = list_idxs[index]
            lx = [cities[c1].x, cities[c2].x]
            ly = [cities[c1].y, cities[c2].y]
            plt.plot(lx, ly)


def find_subtoures(res_x):
    filtered_routes = []

    for index, el in enumerate(copy.deepcopy(res_x)):
        if round(el) == 1:
            filtered_routes.append(list_idxs[index])

    subtoures = []

    tour_idxs_temp = np.zeros(len(cities))

    while len(filtered_routes) > 0:
        subtoures.append([filtered_routes[0]])
        filtered_routes.pop(0)

        for idx, subtour in enumerate(subtoures):
            for subtour_x, subtour_y in subtour:
                for (c1, c2) in filtered_routes:
                    if subtour_x == c1 or subtour_x == c2 or subtour_y == c1 or subtour_y == c2:
                        subtour.append((c1, c2))
                        filtered_routes.remove((c1, c2))

                        tour_idxs_temp[c1] = idx+1
                        tour_idxs_temp[c2] = idx+1

    return tour_idxs_temp


cities = generate_cities()  # generate_test_cities()
cities_range = list(range(len(cities)))
idxs = combinations(cities_range, 2)

dist = calculate_distance()
print("Distanz:", dist)

list_idxs = list(copy.deepcopy(idxs))

Aeq = generate_aeq()
print("Aeq ungesparsed: ", Aeq)

Aeq = csr_matrix(Aeq)
print("Aeq gesparsed: ", Aeq)

beq = np.empty(len(cities))
beq.fill(2)
print("Beq: ", beq)

# dist -> 1D Array von Distanzen alle möglichen Verbindungen bei 200 Städten = 19900 Verbindungen also: 19900 Distanzen
# Aeq -> 200 x 19900 Matrix -> (2,220), x ist Stadt 2 und y 220 ist der Index in der dist Array an dem die Distanz steht
# intcon -> Range von 1 bis Länge von dist
# beq -> 1D Array 200 Lang nur mit 2
# lb und ub
res = linprog(c=dist, A_eq=Aeq, b_eq=beq, bounds=(0, 1), options={'sparse': True})
print(res)

# Zeichne den Graphen mit den Verbindungen
plot_cities()
plot_routes(res.x)

plt.xlim(0, 1)
plt.ylim(0, 1)

plt.xlabel("x")
plt.ylabel("y")

plt.subplots_adjust(left=0.09,
                    bottom=0.09,
                    right=0.9,
                    top=0.9)
plt.show()

tour_idxs = find_subtoures(res.x)
