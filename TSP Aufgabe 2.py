#!/usr/bin/env python
# coding: utf-8

import mip as mip
import numpy as np
from itertools import product
from scipy.optimize import leastsq
import matplotlib.pyplot as plt
import time
import csv


class City:
    """
    Represents a city.

    Attributes
    ----------
    x_coordinate : str
        X coordinate between 0 and 1
    y_coordinate : str
        Y coordinate between 0 and 1
    name : int
        Name of the city displayed as int
    """
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

    city_count = np.random.randint(low=5, high=50)

    for n in range(city_count):
        x_coordinate = round(np.random.uniform(low=0.0, high=1.0), 2)
        y_coordinate = round(np.random.uniform(low=0.0, high=1.0), 2)

        cities_temp.append(City(x_coordinate, y_coordinate, n))

    return cities_temp


# Generiert die Distanzmatrix (c)
def calculate_distance(cities_list):
    cities_distance = []

    for i in range(len(cities_list)):

        city_distance = []

        for j in range(len(cities_list)):

            if i == j:
                city_distance.append(0)
            else:
                distance = ((cities_list[i].x - cities_list[j].x) ** 2 + (
                        cities_list[i].y - cities_list[j].y) ** 2) ** 0.5
                city_distance.append(round(distance, 2))

        cities_distance.append(city_distance)

    return cities_distance


def eval_f(t, x):
    return x[0] * np.exp(-x[1] * t)


def residuals(x, y, t):
    return eval_f(t, x) - y


cities = generate_cities()  # generate_test_cities()  # generate_cities()
c = calculate_distance(cities)
nCities = set(range(len(cities)))

routes = [(i, j) for (i, j) in product(nCities, nCities) if i != j]
print(routes)
print(np.matrix(c))

cities_range = range(len(c))

m = mip.Model()

start = time.time()

x = [[m.add_var(var_type=mip.BINARY) for j in cities_range] for i in cities_range]

# --- Nebenbedingungen aufstellen ---
# Hier wird iterativ jede Zeile betrachtet und geprüft, dass jede Stadt nur einmal angefahren wird.

# Hier iterieren wird pro Zeile immer von links nach rechts.
# Bei 4 Städten lautet list(cities_range) -> [0, 1, 2, 3]
# cities_range_reduced mit i = 0 -> [1, 2, 3]
# cities_range_reduced mit i = 1 -> [0, 2, 3]

# Dadurch entsteht folgende Matrix:

# NUL x20 x30 x40
# x11 NUL x31 x41
# x12 x22 NUL x42
# x13 x23 x33 NUL
for i in list(cities_range):
    cities_range_reduced = list(cities_range).copy()
    cities_range_reduced.remove(i)

    m += mip.xsum(x[j][i] for j in cities_range_reduced) == 1

# Selbe wie oben, nur spaltenweise
for i in set(cities_range):
    cities_range_reduced = list(cities_range).copy()
    cities_range_reduced.remove(i)

    m += mip.xsum(x[i][j] for j in cities_range_reduced) == 1

# Zusätzliche Nebenbedingunge, um Subtouren mit nur 2 Städten zu verhindern
# for (i, j) in routes:
#     m += x[i][j] + x[j][i] <= 1

y = [m.add_var() for z in cities_range]

m.objective = mip.minimize(mip.xsum(c[i][j] * x[i][j] for i in cities_range for j in cities_range))
status = m.optimize()

fig1 = plt.figure("With Subtours")
plt.title("Tour with Subtours")
for idx, city in enumerate(cities):
    plt.scatter(city.x, city.y, s=10)
    plt.annotate(idx, (city.x, city.y))

subtours = []
if m.num_solutions:
    bbs = []
    for idx, city in enumerate(cities):
        single_subtour = []
        if idx in bbs:
            print("Stadt {} schon in einer Subtour besucht.".format(idx));
        else:
            nc = idx
            # print('Subtour {}:'.format(idx))
            # print(' -> Von Punkt: {} = ({},{})'.format(nc, cities[0].x, cities[0].y))
            bbs.append(nc)
            single_subtour.append(nc)
            while True:
                lx = [cities[nc].x]
                ly = [cities[nc].y]
                for i in cities_range:
                    if x[nc][i].x >= 0.99:
                        nc = i
                        break
                lx.append(cities[nc].x)
                ly.append(cities[nc].y)
                plt.plot(lx, ly)
                # print(' -> Zu Punkt: {} = ({},{})'.format(nc, cities[nc].x, cities[nc].y))
                bbs.append(nc)
                single_subtour.append(nc)
                if nc == idx:
                    break
            subtours.append(single_subtour)

print("INITIALE ANZAHL SUBTOUREN: ", len(subtours))

# Solange es mehr als eine Subtour gibt, füge einen Cut in den Cutpool hinzu.
# Cutpool ist eine Funktion von MIP womit, Nebenbedingungen später und bei Bedarf
# zum Model hinzugefügt werden können.

# In dieser Funktion werden immer für alle Citypaare und deren Routen herausgesucht
# die mit der jeweiligen Subtour zu tun haben und für die wird dann die Nebenbedingung
# hinzugefügt
while len(subtours) > 1:
    for subt in subtours:
        single_subt = list(subt.copy())
        single_subt.pop()
        city_pairs = [(i, j) for (i, j) in product(single_subt, single_subt) if i != j]
        for (i, j) in city_pairs:
            if i != j:
                m += mip.xsum(x[i][j] for (i, j) in city_pairs) <= len(single_subt) - 1

    m.objective = mip.minimize(mip.xsum(c[i][j] * x[i][j] for i in cities_range for j in cities_range))
    status = m.optimize()

    subtours = []
    if m.num_solutions:
        bbs = []
        for idx, city in enumerate(cities):
            single_subtour = []
            if idx not in bbs:
                nc = idx
                bbs.append(nc)
                single_subtour.append(nc)
                while True:
                    for i in cities_range:
                        if x[nc][i].x >= 0.99:
                            nc = i
                            break
                    bbs.append(nc)
                    single_subtour.append(nc)
                    if nc == idx:
                        break
                subtours.append(single_subtour)
    print("ANZAHL SUBTOUREN: ", len(subtours))

print("Wegkosten: ", m.objective_value)

end = time.time()

lx = []
ly = []
fig2 = plt.figure("Without Subtours")
plt.title("Tour ohne Subtouren")
for idx, city in enumerate(cities):
    plt.scatter(city.x, city.y, s=10)
    plt.annotate(idx, (city.x, city.y))

for sub in subtours[0]:
    lx.append(cities[sub].x)
    ly.append(cities[sub].y)

plt.plot(lx, ly)

"""After the run the number of cities and the runtime is written to a csv (TSP Aufgabe 2 data.csv)"""
with open('TSP Aufgabe 2 data.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([len(cities), round(end - start, 2)])

"""The data of the csv (TSP Aufgabe 2 data.csv) are displayed in a graph, which shows the runtime analysis"""
with open('TSP Aufgabe 2 data.csv', 'r', newline='') as f:
    reader = csv.reader(f)

    rows = []

    for row in reader:
        rows.append(row)

    if (len(rows)) > 3:
        plt.figure("Runtime analysis")
        plt.title("Runtime analysis")
        plt.xlabel("Cities")
        plt.ylabel("Time")

        rows.sort(key=lambda x: int(x[0]))

        cities = np.array([])
        times = np.array([])
        for row in rows:
            cities = np.append(cities, int(row[0]))
            times = np.append(times, float(row[1]))

        x0 = np.array([0.7, 0.7])
        x, flag = leastsq(residuals, x0, args=(times, cities))

        y_pred = eval_f(cities, x)

        plt.scatter(cities, times, color='red')
        plt.plot(cities, y_pred)

plt.show()
