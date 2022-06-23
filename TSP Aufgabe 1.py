#!/usr/bin/env python
# coding: utf-8

import mip as mip
import numpy as np
from scipy.optimize import leastsq
from itertools import chain, combinations
import matplotlib.pyplot as plt
import copy
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

    city_count = np.random.randint(low=5, high=10)

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


def find_all_possible_subtours(cities):
    """
    Find all possible subtours that can exist.

    Parameters:
       cities (list): Generated cities

    Returns:
       subtours (list): all possible subtours
    """
    cities_range = list(range(len(cities)))

    """
    Example output for 3 Cities:
    [() (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)]
    """
    return list(chain.from_iterable(combinations(cities_range, e) for e in range(len(cities_range) + 1)))


def eval_f(t, x):
    return x[0] * np.exp(-x[1] * t)


def residuals(x, y, t):
    return eval_f(t, x) - y


cities = generate_cities()
distance_matrix = calculate_distance(cities)

"""If there are 10 cities a range is generated: (0, 10)"""
cities_range = range(len(distance_matrix))

m = mip.Model()

start = time.time()

"""Indicating if the Cities (i,j) is used on the route or not"""
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

subtoures = find_all_possible_subtours(cities)
"""The last subtour is the subtour where all the points are in it"""
fullTour = copy.deepcopy(subtoures[-1])
subtoures = subtoures[1:(len(subtoures) - 1)]

"""
For each possible subtour, set the rule that there can never be as many or more routes as cities in the subtour.
This ensures that no subtour can be occurred.
"""
for S in subtoures:
    b = copy.deepcopy(S)
    not_in_S = set(fullTour) - set(b)
    if 2 <= len(S) <= len(fullTour) - 2:
        m += mip.xsum(x[i][j] for i in S for j in not_in_S) >= 1

"""Function to minimize the distance"""
m.objective = mip.minimize(mip.xsum(distance_matrix[i][j] * x[i][j] for i in cities_range for j in cities_range))
status = m.optimize()

fig1 = plt.figure("Optimal Route")
plt.title("Optimal Route")
for idx, city in enumerate(cities):
    plt.scatter(city.x, city.y, s=10)
    plt.annotate(idx, (city.x, city.y))

subtours = []
if m.num_solutions:
    bbs = []
    for idx, city in enumerate(cities):
        single_subtour = []
        if idx in bbs:
            print("City {} already visited in a subtour.".format(idx))
        else:
            nc = idx
            print('Subtour {}:'.format(idx))
            print(' -> From Point: {} = ({},{})'.format(nc, cities[nc].x, cities[nc].y))
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
                print(' -> To Point: {} = ({},{})'.format(nc, cities[nc].x, cities[nc].y))
                bbs.append(nc)
                single_subtour.append(nc)
                if nc == idx:
                    break
            subtours.append(single_subtour)

print("Number of subtoures: ", len(subtours))
print("Road costs: ", m.objective_value)

end = time.time()

"""After the run the number of cities and the runtime is written to a csv (TSP Aufgabe 1 data.csv)"""
with open('TSP Aufgabe 1 data.csv', 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow([len(cities), round(end - start, 2)])

"""The data of the csv (TSP Aufgabe 1 data.csv) are displayed in a graph, which shows the runtime analysis"""
with open('TSP Aufgabe 1 data.csv', 'r', newline='') as f:
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
