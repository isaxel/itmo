import random
import math

dist = [
    [0, 10, 8, 1, 9],
    [10, 0, 5, 8, 5],
    [8, 5, 0, 10, 3],
    [1, 8, 10, 0, 1],
    [9, 5, 3, 1, 0]
]

POP_SIZE = 4
MUTATION_RATE = 0.01
GENERATIONS = 100
ELITE_SIZE = 1

def route_length(route):
    total = 0
    for i in range(len(route) - 1):
        total += dist[route[i]][route[i + 1]]
    total += dist[route[-1]][route[0]]
    return total

def fitness(route):
    return 1 / route_length(route)

def create_route():
    route = list(range(len(dist)))
    random.shuffle(route)
    return route

def selection(population):
    total_fit = sum(fitness(r) for r in population)
    pick = random.uniform(0, total_fit)
    current = 0

    for route in population:
        current += fitness(route)
        if current >= pick:
            return route

def fill_child(child, parent, start, end):
    n = len(parent)
    parent_index = (start + 1) % n
    values = []

    for _ in range(n):
        city = parent[parent_index]

        if city not in child:
            values.append(city)

        parent_index = (parent_index + 1) % n

    value_index = 0

    for i in range(n):
        if child[i] is None:
            child[i] = values[value_index]
            value_index += 1

def crossover(parent1, parent2):
    n = len(parent1)

    while True:
        start, end = sorted(random.sample(range(1, n), 2))
        if end - start >= 2:
            break

    child1 = [None] * n
    child2 = [None] * n

    child1[start:end] = parent2[start:end]
    child2[start:end] = parent1[start:end]

    fill_child(child1, parent1, start, end)
    fill_child(child2, parent2, start, end)

    return child1, child2

def mutate(route):
    if random.random() < MUTATION_RATE:
        i, j = random.sample(range(len(route)), 2)
        route[i], route[j] = route[j], route[i]
    return route

def genetic_algorithm():
    population = [create_route() for _ in range(POP_SIZE)]

    for generation in range(GENERATIONS):
        population = sorted(population, key=route_length)

        new_population = population[:ELITE_SIZE]

        while len(new_population) < POP_SIZE:
            p1 = selection(population)
            p2 = selection(population)

            child1, child2 = crossover(p1, p2)

            child1 = mutate(child1)
            child2 = mutate(child2)

            new_population.append(child1)

            if len(new_population) < POP_SIZE:
                new_population.append(child2)

        population = new_population

    best = min(population, key=route_length)
    return best, route_length(best)

best_route, best_distance = genetic_algorithm()

print("Генетический алгоритм")
print("Лучший маршрут:", " -> ".join(f"Город {i + 1}" for i in best_route), "->", f"Город {best_route[0] + 1}")
print("Длина маршрута:", best_distance)


graph = {
    "A": {"B": 13, "C": 7, "F": 7},
    "B": {"A": 13},
    "C": {"A": 7, "D": 8, "E": 8},
    "D": {"C": 8, "E": 11, "G": 11},
    "E": {"C": 8, "D": 11, "G": 19},
    "F": {"A": 7, "G": 38},
    "G": {"D": 11, "E": 19, "F": 38}
}

ANTS = 20
ITERATIONS = 100
ALPHA = 1
BETA = 2
EVAPORATION = 0.5
Q = 100
START = "A"
END = "G"

pheromone = {}
for u in graph:
    for v in graph[u]:
        pheromone[(u, v)] = 1.0

def choose_next(current, visited):
    variants = []

    for neighbor, distance in graph[current].items():
        if neighbor not in visited:
            tau = pheromone[(current, neighbor)] ** ALPHA
            eta = (1 / distance) ** BETA
            variants.append((neighbor, tau * eta))

    if not variants:
        return None

    total = sum(value for _, value in variants)
    r = random.uniform(0, total)
    current_sum = 0

    for neighbor, value in variants:
        current_sum += value
        if current_sum >= r:
            return neighbor

def path_length(path):
    return sum(graph[path[i]][path[i + 1]] for i in range(len(path) - 1))

def ant_colony():
    best_path = None
    best_len = math.inf

    global pheromone

    for iteration in range(ITERATIONS):
        all_paths = []

        for ant in range(ANTS):
            current = START
            visited = {START}
            path = [START]

            while current != END:
                next_node = choose_next(current, visited)

                if next_node is None:
                    break

                path.append(next_node)
                visited.add(next_node)
                current = next_node

            if path[-1] == END:
                length = path_length(path)
                all_paths.append((path, length))

                if length < best_len:
                    best_len = length
                    best_path = path

        for edge in pheromone:
            pheromone[edge] *= (1 - EVAPORATION)

        for path, length in all_paths:
            deposit = Q / length
            for i in range(len(path) - 1):
                u = path[i]
                v = path[i + 1]
                pheromone[(u, v)] += deposit
                pheromone[(v, u)] += deposit

    return best_path, best_len

aco_path, aco_len = ant_colony()

print("\nМуравьиная колония")
print("Лучший путь:", " -> ".join(aco_path))
print("Длина пути:", aco_len)