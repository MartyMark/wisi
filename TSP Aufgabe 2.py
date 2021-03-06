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


def generate_test_cities():
    """
    Generates static test data.

    Returns:
        cities (array): 4 Cities
    """
    return [
        City(0.1, 0.1, 0),
        City(0.1, 0.6, 1),
        City(0.6, 0.2, 2),
        City(0.8, 0.9, 3)
    ]


def generate_cities():
    """
    Generates the cities containing the x and y coordinate between 0 and 1.

    Returns:
        cities_temp (list): Randomly generated cities
    """
    cities_temp = []

    city_count = np.random.randint(low=5, high=7)

    for n in range(city_count):
        x_coordinate = round(np.random.uniform(low=0.0, high=1.0), 2)
        y_coordinate = round(np.random.uniform(low=0.0, high=1.0), 2)

        cities_temp.append(City(x_coordinate, y_coordinate, n))

    return cities_temp


def calculate_distance(cities):
    """
    Generates the distance matrix.

    Parameters:
        cities (list): Generated cities

    Returns:
        cities_temp (list): Randomly generated cities
    """
    cities_distance = []

    for i in range(len(cities)):

        city_distance = []

        for j in range(len(cities)):

            if i == j:
                city_distance.append(0)
            else:
                distance = ((cities[i].x - cities[j].x) ** 2 + (
                        cities[i].y - cities[j].y) ** 2) ** 0.5
                city_distance.append(round(distance, 2))

        cities_distance.append(city_distance)

    return cities_distance


def eval_f(t, x):
    return x[0] * np.exp(-x[1] * t)


def residuals(x, y, t):
    return eval_f(t, x) - y


cities = generate_cities()
distance_matrix = calculate_distance(cities)

cities_range = range(len(cities))

"""Create the set for the combination list of cities. For 8 cities the set looks like this: {0, 1, 2, 3, 4, 5, 6, 7}"""
nCities = set(cities_range)

m = mip.Model()

start = time.time()

x = [[m.add_var(var_type=mip.BINARY) for j in cities_range] for i in cities_range]

"""
Constraints
----------
Here, each line is considered iteratively and it is checked that each city is approached only once.

Here we iterate per line always from left to right.
For 4 cities it reads: list(cities_range) -> [0, 1, 2, 3]
# cities_range_reduced with i = 0 -> [1, 2, 3]
# cities_range_reduced with i = 1 -> [0, 2, 3]

# This results in the following matrix:

# NUL x11 x12 x13
# x11 NUL x22 x23
# x12 x22 NUL x33
# x13 x23 x33 NUL

In the for loop, we iterate effected through each decision variable that determines whether the route is 
part of the tour, thereby constraining the exit from each city only once
"""
for i in list(cities_range):
    cities_range_reduced = list(cities_range).copy()
    cities_range_reduced.remove(i)

    m += mip.xsum(x[j][i] for j in cities_range_reduced) == 1

"""Here, each line is considered iteratively and it is checked that each city is entered only once"""
for i in set(cities_range):
    cities_range_reduced = list(cities_range).copy()
    cities_range_reduced.remove(i)

    m += mip.xsum(x[i][j] for j in cities_range_reduced) == 1

"""Function to minimize the distance"""
m.objective = mip.minimize(mip.xsum(distance_matrix[i][j] * x[i][j] for i in cities_range for j in cities_range))
status = m.optimize()

fig1 = plt.figure("With Subtours")
plt.title("Tour with Subtours")
for idx, city in enumerate(cities):
    plt.scatter(city.x, city.y, s=10)
    plt.annotate(idx, (city.x, city.y))

"""Here all existing subtours are selected and the routes between the cities are plotted."""
subtours = []
if m.num_solutions:
    already_visited_city = []
    for idx, city in enumerate(cities):
        single_subtour = []
        if idx not in already_visited_city:
            ci = idx
            already_visited_city.append(ci)
            single_subtour.append(ci)
            while True:
                lx = [cities[ci].x]
                ly = [cities[ci].y]
                for i in cities_range:
                    if x[ci][i].x >= 0.99:
                        ci = i
                        break
                lx.append(cities[ci].x)
                ly.append(cities[ci].y)
                plt.plot(lx, ly)
                already_visited_city.append(ci)
                single_subtour.append(ci)
                if ci == idx:
                    break
            subtours.append(single_subtour)

print("Initial number of subtoures:", len(subtours))
"""
If there are more than one Subtour, for every Subtour find all corresponding Citiespairs and their routes. 
For all possible Routes in the Subtour add a Constraint to eliminate the Subtour.

Contraint:
    If a Subtour consist of 3 Cities, allow only to Routes between these 3 Cities
    
After adding the Constraints solve the Function again and repeat the process until only one
Subtour is found.
"""
while len(subtours) > 1:
    for subt in subtours:
        single_subt = list(subt.copy())
        single_subt.pop()
        city_pairs = [(i, j) for (i, j) in product(single_subt, single_subt) if i != j]
        for (i, j) in city_pairs:
            if i != j:
                m += mip.xsum(x[i][j] for (i, j) in city_pairs) <= len(single_subt) - 1

    m.objective = mip.minimize(mip.xsum(distance_matrix[i][j] * x[i][j] for i in cities_range for j in cities_range))
    status = m.optimize()

    """Here all existing subtours are selected and the routes between the cities are plotted."""
    subtours = []
    if m.num_solutions:
        already_visited_city = []
        for idx, city in enumerate(cities):
            single_subtour = []
            if idx not in already_visited_city:
                ci = idx
                already_visited_city.append(ci)
                single_subtour.append(ci)
                while True:
                    for i in cities_range:
                        if float(x[ci][i].x) >= 0.99:
                            ci = i
                            break
                    already_visited_city.append(ci)
                    single_subtour.append(ci)
                    if ci == idx:
                        break
                subtours.append(single_subtour)
        print("Number of subtoures:", len(subtours))

print("Final Number of subtoures: ", len(subtours))
print("Road costs: ", m.objective_value)

end = time.time()

lx = []
ly = []
fig2 = plt.figure("Without Subtours")
plt.title("Tour without Subtours")
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
