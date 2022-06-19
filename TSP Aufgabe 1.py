#!/usr/bin/env python
# coding: utf-8

import matplotlib
import mip as mip
import numpy as np
from itertools import product, chain, combinations
import matplotlib.pyplot as plt
import copy


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

    city_count = np.random.randint(low=12, high=13)

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

#Finde alle möglichen Subtouren die es geben kann.
def findAllPossibleSubtours(iter):
    "Subtour([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iter)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

cities = generate_cities() #generate_test_cities()  # generate_cities()
c = calculate_distance(cities)
nCities = set(range(len(cities)))

DFsubtours = list(findAllPossibleSubtours(range(len(nCities))))
DFsubtours = DFsubtours[1:(len(DFsubtours)-1)]

cities_range = range(len(c))

m = mip.Model()

x = [[m.add_var(var_type=mip.BINARY) for j in cities_range] for i in cities_range]

for i in list(cities_range):
    cities_range_reduced = list(cities_range).copy()
    cities_range_reduced.remove(i)

    m += mip.xsum(x[j][i] for j in cities_range_reduced) == 1
    
# Selbe wie oben, nur spaltenweise
for i in set(cities_range):
    cities_range_reduced = list(cities_range).copy()
    cities_range_reduced.remove(i)

    m += mip.xsum(x[i][j] for j in cities_range_reduced) == 1

#Für jede mögliche Subtour, lege die Regel fest, dass es niemals genauso viele oder mehr 
#Routen wie Städte in der Subtour geben kann. Dadurch ist gewähleistet, dass keine Subtour
#entstehen kann.    
for S in DFsubtours:
    m += mip.xsum(x[i][j] for i in S for j in S) <= len(S)-1

y = [m.add_var() for z in cities_range]

m.objective = mip.minimize(mip.xsum(c[i][j] * x[i][j] for i in cities_range for j in cities_range))
status = m.optimize()

fig1 = plt.figure("Optimal Route")
plt.title("Optimalste Route")
for idx, city in enumerate(cities):
    plt.scatter(city.x, city.y, s=10)
    plt.annotate(idx, (city.x,city.y))
    
subtours = []
if m.num_solutions:
    bbs = []
    for idx, city in enumerate(cities):
        single_subtour = []
        if idx in bbs:
            print("Stadt {} schon in einer Subtour besucht.".format(idx));
        else:
            nc = idx
            print('Subtour {}:'.format(idx))
            print(' -> Von Punkt: {} = ({},{})'.format(nc, cities[nc].x, cities[nc].y))
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
                plt.plot(lx,ly) 
                print(' -> Zu Punkt: {} = ({},{})'.format(nc, cities[nc].x, cities[nc].y))
                bbs.append(nc)
                single_subtour.append(nc)
                if nc == idx:
                    break
            subtours.append(single_subtour)

print("INITIALE ANZAHL SUBTOUREN: ", len(subtours))
print("Wegkosten: ", m.objective_value)

