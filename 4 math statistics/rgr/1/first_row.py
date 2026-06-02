import csv
import numpy as np
import matplotlib.pyplot as plt

def spred_func(n,mas):
    y = np.arange(1, n+1) / n

    plt.step(mas, y, where='post', linewidth=2)
    plt.scatter(mas, y, color='red', s=50)

    plt.xlabel('x')
    plt.ylabel('F_n(x)')
    plt.title('Эмпирическая функция распределения')
    plt.grid(True)
    plt.ylim(0, 1.1)
    plt.show()

def calculate_stats(n,data_sorted):

    #выборочное среднее
    vub_avg = sum(data_sorted) / n

    #дисперсии
    #смещенная (делим на n)
    var_biased = sum((x - vub_avg)**2 for x in data_sorted) / n

    #несмещенная (делим на n-1)
    var_unbiased = sum((x - vub_avg)**2 for x in data_sorted) / (n - 1)

    #стандартные отклонения
    std_biased = var_biased ** 0.5
    std_unbiased = var_unbiased ** 0.5

    #медиана
    if n % 2 == 1:
        median = data_sorted[n // 2]
    else:
        median = (data_sorted[n // 2 - 1] + data_sorted[n // 2]) / 2

    #квартили
    q1_index = int(n * 0.25)
    q3_index = int(n * 0.75)
    q1 = data_sorted[q1_index]
    q3 = data_sorted[q3_index]

    stats = {
        'n': n,
        'vub_avg': vub_avg,
        'var_biased': var_biased,
        'var_unbiased': var_unbiased,
        'std_biased': std_biased,
        'std_unbiased': std_unbiased,
        'median': median,
        'q1': q1,
        'q3': q3,
        'min': data_sorted[0],
        'max': data_sorted[-1],
        'range': data_sorted[-1] - data_sorted[0]
    }

    return stats

#Гистограмма с правилом Скотта: h = 3.5 * S * n^(-1/3)
def hist_scott(n,data,std_unbiased):

    #ширина интервала
    h = 3.5 * std_unbiased * n**(-1/3)

    #число интервалов
    k = int((max(data) - min(data)) / h) + 1

    plt.hist(data, bins=k, edgecolor='black')
    plt.xlabel('Значения')
    plt.ylabel('Частота')
    plt.title(f'Правило Скотта (интервалов = {k})')
    plt.grid(True, alpha=0.3)
    plt.show()

    return k


#Гистограмма с правилом Фридмана-Диакониса: h = 2 * IQR * n^(-1/3)
def hist_fd(n,data, q1,q3):

    iqr = q3 - q1

    #ширина интервала
    h = 2 * iqr * n**(-1/3)

    #число интервалов
    k = int((max(data) - min(data)) / h) + 1

    plt.hist(data, bins=k, edgecolor='black')
    plt.xlabel('Значения')
    plt.ylabel('Частота')
    plt.title(f'Правило Фридмана-Диакониса (интервалов = {k})')
    plt.grid(True, alpha=0.3)
    plt.show()

    return k

#оценка нормального распределения методами мм и ммп
def estimate_normal(data):
    n = len(data)
    mean = sum(data) / n
    var = sum((x - mean)**2 for x in data) / n
    S = var ** 0.5 # выборочное стандартное отклонение

    # метод моментов
    a_mm = mean
    sigma_mm = S

    # метод максимального правдоподобия
    a_mle = mean
    sigma_mle = S

    return {
        "MM": (a_mm, sigma_mm),
        "MLE": (a_mle, sigma_mle)
    }

# оценка равномерного распределения
def estimate_uniform(data):
    n = len(data)
    mean = sum(data) / n
    var = sum((x - mean)**2 for x in data) / n
    S = var ** 0.5

    # MM
    a_mm = mean - (3 * var) ** 0.5
    b_mm = mean + (3 * var) ** 0.5

    # ММП
    a_mle = min(data)
    b_mle = max(data)

    return {
        "MM": (a_mm, b_mm),
        "MLE": (a_mle, b_mle)
    }

#оценка экспоненциального распределения
def estimate_exponential(data):
    n = len(data)
    mean = sum(data) / n
    var = sum((x - mean)**2 for x in data) / n
    S = var ** 0.5

    # MM
    lam_mm = 1 / S
    c_mm = mean - (1 / lam_mm)

    #ММП
    c_mle = min(data)
    lam_mle = 1 / (mean - c_mle)

    return {
        "MM": {"lambda": lam_mm, "c": c_mm},
        "MLE": {"lambda": lam_mle, "c": c_mle}
    }

#сравнивает оценки
def compare(name, result):

    print("\n", name)

    print("Метод моментов:", result["MM"])
    print("Метод максимального правдоподобия:", result["MLE"])

#функция для анализа одного ряда(пункт 1-2)
def analyze_one(data):
    #вариационный ряд
    sorted_data=sorted(data)
    n=200

    #вызывают ффункцию для функции распределения
    spred_func(n,sorted_data)

    #считаем основные значения
    stats = calculate_stats(n,sorted_data)
    print(stats)

    #строим гистограммы
    q1=stats['q1']
    q3=stats['q3']
    std_unbiased=stats['std_unbiased']

    hist_scott(n,sorted_data,std_unbiased)
    hist_fd(n,data,q1,q3)


X1,X2,X3,X4 = [],[],[],[]

with open('RGR1_A-5_X1-X4.csv', 'r') as file:
    reader = csv.reader((file))
    next(reader)
    for row in file:
        temp = row.split(",")
        if (temp[0]=="X1"):
            break
        X1.append(float(temp[0]))
        X2.append(float(temp[1]))
        X3.append(float(temp[2]))
        X4.append(float(temp[3]))

analyze_one(X1)
analyze_one(X2)
analyze_one(X3)

compare("Exponential", estimate_exponential(X1))
# compare("Uniform", estimate_uniform(X2))
# compare("Normal", estimate_normal(X3))
