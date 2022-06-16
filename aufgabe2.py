import matplotlib
import mip as mip
import numpy as np
from itertools import product
import matplotlib.pyplot as plt
from scipy.optimize import linprog

matplotlib.use('TkAgg')


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

    city_count = np.random.randint(low=4, high=5)

    for n in range(city_count):
        x_coordinate = round(np.random.uniform(low=0.0, high=1.0), 2)
        y_coordinate = round(np.random.uniform(low=0.0, high=1.0), 2)

        cities_temp.append(City(x_coordinate, y_coordinate, n))

    return cities_temp


# Generiert die Distanzmatrix (c)
def calculate_distance(cities_list):
    cities_distance = []

    for i in range(len(cities_list)):
        for j in range(len(cities_list)):

            if i == j:
                cities_distance.append(0)
            else:
                distance = ((cities_list[i].x - cities_list[j].x) ** 2 + (
                        cities_list[i].y - cities_list[j].y) ** 2) ** 0.5
                cities_distance.append(round(distance, 2))

    return cities_distance


cities = generate_test_cities()  # generate_cities()
dist = calculate_distance(cities)

print(dist)

# Ausgabe der einzelnen Punkte mit deren Koordinaten
for point in cities:
    print("Punkt: {}: ({},{})".format(point.name, point.x, point.y))

# dist -> 1D Array von Distanzen alle möglichen Verbindungen bei 200 Städten = 19900 Verbindungen also: 19900 Distanzen
# Aeq -> 200 x 19900 Matrix -> (2,220), x ist Stadt 2 und y 220 ist der Index in der dist Array an dem die Distanz steht
# intcon -> Range von 1 bis Länge von dist
# beq -> 1D Array 200 Lang nur mit 2
# lb und ub

[x_tsp, costopt, exitflag, output] = linprog(dist, intcon, [], [], Aeq, beq, lb, ub, opts);
