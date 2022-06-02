import matplotlib
import mip as mip
import numpy as np
from itertools import product
# import networkx as nx
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')


class City:
    def __init__(self, x_coordinate, y_coordinate, name):
        self.x = x_coordinate
        self.y = y_coordinate
        self.name = name


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


cities = generate_cities()
c = calculate_distance(cities)

# Ausgabe der einzelnen Punkte mit deren Koordinaten
for point in cities:
    print("Punkt: {}: ({},{})".format(point.name,point.x, point.y))

# Ausgabe der Distanzmatrix    
print(np.matrix(c))

# Wenn es 10 Städte gibt wird eine Range erzeugt: (0, 10)
cities_range = range(len(c))

m = mip.Model()

x = [[m.add_var(var_type=mip.BINARY) for j in cities_range] for i in cities_range]

# Jede Stadt hat eine andere fortlaufende Nummer in der geplanten Route, außer der ersten
y = [m.add_var() for z in cities_range]

# --- Nebenbedingungen aufstellen ---
# TODO So umbauen, dass es einfacher zu lesen ist.

# Hier wird iterativ jede Spalte betrachtet und geprüft, dass jede Stadt nur einmal angefahren wird.
for i in set(cities_range):
    m += mip.xsum(x[j][i] for j in set(cities_range) - {i}) == 1

# Hier wird iterativ jede Spalte betrachtet und geprüft, dass jede Stadt nur einmal verlassen wird.    
for i in set(cities_range):
    m += mip.xsum(x[i][j] for j in set(cities_range) - {i}) == 1
# Hier ist der Constraint um Subtouren zu vermeiden  
for (i, j) in product(set(cities_range) - {0}, set(cities_range) - {0}):
    if i != j:
        m += y[i] - (len(c)+1)*x[i][j] >= y[j]-len(c)

# Zielfunktion mip.xsum(c[i][j] * x[i][j] minimieren
m.objective = mip.minimize(mip.xsum(c[i][j] * x[i][j] for i in cities_range for j in cities_range))
status = m.optimize()


# print('solution:')
# for v in m.vars:
#     print('{} : {}'.format(v.name, v.x))

# print('Gesamtkosten des Weges: {}'.format(m.objective_value))

plt.style.use('_mpl-gallery')
plt.rcParams["figure.figsize"] = (6, 6)
#TODO: Funktion und Variablennamen umändern. Dies ist nur zur Demonstration wie es am ende funktionieren muss.
if m.num_solutions:
    nc = 0
    print('Optimaler Weg ist folgender:')
    print(' -> Von Punkt: {} = ({},{})'.format(nc, cities[0].x, cities[0].y))
    while True:
        plt.scatter(cities[nc].x, cities[nc].y, s=10)
        plt.annotate(nc, xytext=(cities[nc].x, cities[nc].y), xy=(cities[[i for i in cities_range if x[nc][i].x >= 0.99][0]].x, cities[[i for i in cities_range if x[nc][i].x >= 0.99][0]].y), arrowprops=dict(arrowstyle='->'))
        nc = [i for i in cities_range if x[nc][i].x >= 0.99][0]
        print(' -> Zu Punkt: {} = ({},{})'.format(nc, cities[nc].x, cities[nc].y))
        if nc == 0:
            break
    print('Gesamtdistanz des Weges: {}'.format(m.objective_value))

# Plotting
# plt.style.use('_mpl-gallery')
# plt.rcParams["figure.figsize"] = (6, 6)

# TODO Hier müssen dann die sortieren Cities rein
# for i, city in enumerate(cities):
#     plt.annotate(city.name, (city.x, city.y))
#     plt.scatter(city.x, city.y, s=10)
#     if i == len(cities) - 1:
#         plt.annotate(
#             '',
#             xytext=(city.x, city.y),
#             xy=(cities[0].x, cities[0].y),
#             arrowprops=dict(arrowstyle='->')
#         )
#     else:
#         plt.annotate(
#             '',
#             xytext=(city.x, city.y),
#             xy=(cities[i + 1].x, cities[i + 1].y),
#             arrowprops=dict(arrowstyle='->')
#         )

plt.xlim(0, 1)
plt.ylim(0, 1)

plt.xlabel("x")
plt.ylabel("y")

plt.subplots_adjust(left=0.09,
                    bottom=0.09,
                    right=0.9,
                    top=0.9)
plt.show()
