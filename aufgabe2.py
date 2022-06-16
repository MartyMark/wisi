import matplotlib
import mip as mip
import numpy as np
from itertools import product, combinations, tee
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


def calculate_distance():
    cities_distance = []
    for (i,j) in combinations(cities_range,2):
        print(i, " " ,j)
        print("City 1 (",cities[i].x, ",", cities[i].y, ") ", "City 2 (", cities[j].x, ", ", cities[j].y, ")")
        
        distance = ((cities[i].x - cities[j].x) ** 2 + (
                cities[i].y - cities[j].y) ** 2) ** 0.5
        print(distance)
        cities_distance.append(round(distance, 2))
    
    return cities_distance

def generate_Aeq():
    Aeq = []   
    iterIdxs = tee(idxs, len(cities))
    for i in range(len(cities)):
        single_aeq = []
        for (k, j) in iterIdxs[i]:
            if i == k or i == j:
                single_aeq.append(1)
            else:
                single_aeq.append(0)
        Aeq.append(single_aeq)
    return Aeq


cities = generate_test_cities()  # generate_cities()
cities_range = list(range(len(cities)))
idxs = combinations(cities_range,2)

dist = calculate_distance()
print("Distanz:", dist)

# def test():
#     single_aeq = []
#     for (k, j) in test2[]:
#         print(k, " ", j)
#         if i == k or i == j:
#             single_aeq.append(1)
#         else:
#             single_aeq.append(0)
#     return single_aeq

Aeq = generate_Aeq() 
print(Aeq)  
# for i in range(len(cities)):
#     print(i)
#     single_aeq = []
#     # single_aeq = []
#     # for (k, j) in idxs:
#     #     print(k, " ", j)
#     #     if i == k or i == j:
#     #         single_aeq.append(1)
#     #     else:
#     #         single_aeq.append(0)
#     for (k, j) in test2[i]:
#         print(k, " ", j)
#         if i == k or i == j:
#             single_aeq.append(1)
#         else:
#             single_aeq.append(0)
#     Aeq.append(single_aeq)

# print(Aeq)


    
            
    
    
# Ausgabe der einzelnen Punkte mit deren Koordinaten
# for point in cities:
#     print("Punkt: {}: ({},{})".format(point.name, point.x, point.y))

# dist -> 1D Array von Distanzen alle möglichen Verbindungen bei 200 Städten = 19900 Verbindungen also: 19900 Distanzen
# Aeq -> 200 x 19900 Matrix -> (2,220), x ist Stadt 2 und y 220 ist der Index in der dist Array an dem die Distanz steht
# intcon -> Range von 1 bis Länge von dist
# beq -> 1D Array 200 Lang nur mit 2
# lb und ub

# Aeq = [[1,1,1]
        

# [x_tsp, costopt, exitflag, output] = linprog(dist, intcon, [], [], Aeq, beq, lb, ub, opts);
