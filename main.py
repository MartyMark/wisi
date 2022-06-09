import matplotlib
import mip as mip
import numpy as np
from itertools import product
import matplotlib.pyplot as plt

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


cities = generate_test_cities()  # generate_cities()
c = calculate_distance(cities)

# Ausgabe der einzelnen Punkte mit deren Koordinaten
for point in cities:
    print("Punkt: {}: ({},{})".format(point.name, point.x, point.y))

# Ausgabe der Distanzmatrix    
print(np.matrix(c))

# Wenn es 10 Städte gibt wird eine Range erzeugt: (0, 10)
cities_range = range(len(c))

m = mip.Model()

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

# Hier wird iterativ jede Spalte betrachtet und geprüft, dass jede Stadt nur einmal verlassen wird.

# Selbe wie oben, nur spaltenweise
for i in set(cities_range):
    cities_range_reduced = list(cities_range).copy()
    cities_range_reduced.remove(i)

    m += mip.xsum(x[i][j] for j in cities_range_reduced) == 1

# Hier ist die Nebenbedingung um Subtouren zu vermeiden. Die Funktion product erzeugt einen Iterator,
# der das kartesische Produkt der übergebenen iterierbaren Objekte durchläuft.

# Jede Stadt hat eine andere fortlaufende Nummer in der geplanten Route, außer der ersten
y = [m.add_var() for z in cities_range]

cities_range_reduced = list(cities_range).copy()
cities_range_reduced.remove(0)
# Bei 4 Städten lautet product(cities_range_reduced, cities_range_reduced
# -> [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), ... ]
for (i, j) in product(cities_range_reduced, cities_range_reduced):
    if i != j:
        m += y[i] - (len(c) + 1) * x[i][j] >= y[j] - len(c)

# --- Zielfunktion ---
# mip.xsum(c[i][j] * x[i][j] minimieren
m.objective = mip.minimize(mip.xsum(c[i][j] * x[i][j] for i in cities_range for j in cities_range))
status = m.optimize()

# --- Plotting ---
plt.style.use('_mpl-gallery')
plt.rcParams["figure.figsize"] = (6, 6)
# TODO: Funktion und Variablennamen umändern. Dies ist nur zur Demonstration wie es am ende funktionieren muss.
if m.num_solutions:
    nc = 0
    print('Optimaler Weg ist folgender:')
    print(' -> Von Punkt: {} = ({},{})'.format(nc, cities[0].x, cities[0].y))
    while True:
        plt.scatter(cities[nc].x, cities[nc].y, s=10)
        plt.annotate(
            nc,
            xytext=(cities[nc].x, cities[nc].y),
            xy=(
                cities[[i for i in cities_range if x[nc][i].x >= 0.99][0]].x,
                cities[[i for i in cities_range if x[nc][i].x >= 0.99][0]].y
            ),
            arrowprops=dict(arrowstyle='->')
        )
        nc = [i for i in cities_range if x[nc][i].x >= 0.99][0]
        print(' -> Zu Punkt: {} = ({},{})'.format(nc, cities[nc].x, cities[nc].y))
        if nc == 0:
            break
    print('Gesamtdistanz des Weges: {}'.format(m.objective_value))

plt.xlim(0, 1)
plt.ylim(0, 1)

plt.xlabel("x")
plt.ylabel("y")

plt.subplots_adjust(left=0.09,
                    bottom=0.09,
                    right=0.9,
                    top=0.9)
plt.show()
