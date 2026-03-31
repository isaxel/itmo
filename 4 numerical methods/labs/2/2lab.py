import math
import matplotlib.pyplot as plt


def input_float(prompt):
    while True:
        s = input(prompt).strip()

        s = s.replace(',', '.')

        if s.count('.') > 1:
            print("Ошибка! Некорректный формат числа.")
            continue

        if s in ("", ".", "-", "+", "-.", "+."):
            print("Ошибка! Введите число.")
            continue

        try:
            return float(s)
        except:
            print("Ошибка! Некорректный ввод числа.")


def input_int(prompt, min_val, max_val):
    while True:
        try:
            val = int(input(prompt))
            if min_val <= val <= max_val:
                return val
            else:
                print(f"Введите число от {min_val} до {max_val}")
        except:
            print("Ошибка! Введите целое число.")


def f1(x): return x**3 - x - 2
def f2(x): return math.sin(x) - x/2
def f3(x): return x**3 - 3*x + 1
def f4(x): return math.cos(x) - x


functions = {
    1: ("x^3 - x - 2", f1),
    2: ("sin(x) - x/2", f2),
    3: ("x^3 - 3x + 1", f3),
    4: ("cos(x) - x", f4)
}


def read_from_file_equation(filename):
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()

        # формат файла:
        # a b eps
        a, b, eps = map(lambda x: float(x.replace(',', '.')), lines[0].split())

        return a, b, eps
    except:
        print("Ошибка чтения файла!")
        return None


def write_to_file(filename, text):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)


def derivative(f, x):
    h = 1e-6
    return (f(x + h) - f(x)) / h


def check_root(f, a, b):
    if f(a) * f(b) > 0:
        return False
    return True


def chord_method(f, a, b, eps):
    x0 = a if f(a)*derivative(f, a) > 0 else b
    fixed = b if x0 == a else a

    x = x0
    it = 0

    while True:
        x_new = x - f(x)*(x - fixed)/(f(x) - f(fixed))
        it += 1
        if abs(x_new - x) < eps:
            return x_new, it
        x = x_new


def secant_method(f, a, b, eps):
    x0, x1 = a, b
    it = 0

    while True:
        x2 = x1 - f(x1)*(x1 - x0)/(f(x1) - f(x0))
        it += 1
        if abs(x2 - x1) < eps:
            return x2, it
        x0, x1 = x1, x2


def newton_method(f, a, b, eps):
    x = a if f(a)*derivative(f, a) > 0 else b
    it = 0

    while True:
        x_new = x - f(x)/derivative(f, x)
        it += 1
        if abs(x_new - x) < eps:
            return x_new, it
        x = x_new


def phi(x):
    return math.cos(x)


def check_convergence(phi, a, b):
    h = 1e-5
    for x in [a + i*(b-a)/100 for i in range(101)]:
        d = (phi(x+h) - phi(x)) / h
        if abs(d) >= 1:
            return False
    return True


def simple_iteration(a, b, eps):
    if not check_convergence(phi, a, b):
        print("Метод не сходится!")
        return None, 0

    x = (a + b)/2
    it = 0

    while True:
        x_new = phi(x)
        it += 1
        if abs(x_new - x) < eps:
            return x_new, it
        x = x_new


def plot_function(f, a, b, save=False, filename="graph.png"):
    xs = [a + i*(b-a)/1000 for i in range(1000)]
    ys = [f(x) for x in xs]

    plt.figure()
    plt.plot(xs, ys)
    plt.axhline(0)
    plt.title("График функции")

    if save:
        plt.savefig(filename)
        print(f"График сохранён в {filename}")
    else:
        plt.show()


def solve_equation():
    print("\nВыберите функцию:")
    for k, v in functions.items():
        print(f"{k}. {v[0]}")

    choice = input_int("Ваш выбор: ", 1, len(functions))
    name, f = functions[choice]

    # график до ввода
    plot_function(f, -10, 10)

    print("\nИсточник данных:")
    print("1. С клавиатуры")
    print("2. Из файла")

    source = input_int("Ваш выбор: ", 1, 2)

    if source == 1:
        a = input_float("Введите a: ")
        b = input_float("Введите b: ")
        eps = input_float("Введите точность: ")
    else:
        filename = input("Введите имя файла: ")
        data = read_from_file_equation(filename)
        if data is None:
            return
        a, b, eps = data

    if a > b:
        a, b = b, a

    if not check_root(f, a, b):
        print("Нет корня на интервале!")
        return

    print("\nМетоды:")
    print("1. Хорд")
    print("2. Секущих")
    print("3. Ньютона")
    print("4. Простых итераций")

    m = input_int("Ваш выбор: ", 1, 4)

    if m == 1:
        root, it = chord_method(f, a, b, eps)
    elif m == 2:
        root, it = secant_method(f, a, b, eps)
    elif m == 3:
        root, it = newton_method(f, a, b, eps)
    else:
        root, it = simple_iteration(a, b, eps)

    result_text = f"""
Функция: {name}
Интервал: [{a}, {b}]
Корень: {root}
f(x): {f(root)}
Итерации: {it}
"""

    print("\nКуда вывести результат?")
    print("1. На экран")
    print("2. В файл")

    out = input_int("Ваш выбор: ", 1, 2)

    if out == 1:
        print(result_text)
        plot_function(f, a, b)
    else:
        filename = input("Имя файла: ")
        write_to_file(filename, result_text)
        plot_function(f, a, b, save=True, filename="graph.png")


def system1(x, y):
    return math.sin(x+y) - 1.4*x, x**2 + y**2 - 1


def newton_system(x, y, eps):
    it = 0
    while True:
        f1, f2 = system1(x, y)

        J = [
            [math.cos(x+y) - 1.4, math.cos(x+y)],
            [2*x, 2*y]
        ]

        det = J[0][0]*J[1][1] - J[0][1]*J[1][0]

        if abs(det) < 1e-10:
            raise ValueError("Ошибка: Якобиан вырожден (det = 0). Выберите другое начальное приближение.")

        dx = (-f1*J[1][1] + f2*J[0][1]) / det
        dy = (-J[0][0]*f2 + J[1][0]*f1) / det

        x_new = x + dx
        y_new = y + dy

        it += 1

        if max(abs(x_new-x), abs(y_new-y)) < eps:
            return x_new, y_new, it

        x, y = x_new, y_new


def plot_system(save=False, filename="system.png"):
    import numpy as np

    x = np.linspace(-2, 2, 400)
    y = np.linspace(-2, 2, 400)

    X, Y = np.meshgrid(x, y)

    Z1 = np.sin(X + Y) - 1.4 * X
    Z2 = X**2 + Y**2 - 1

    plt.figure()
    plt.contour(X, Y, Z1, levels=[0])
    plt.contour(X, Y, Z2, levels=[0])

    if save:
        plt.savefig(filename)
    else:
        plt.show()


def solve_system():
    print("\nРешаем систему:")
    print("sin(x+y) - 1.4x = 0")
    print("x^2 + y^2 = 1")

    print("\nПостроение графика системы...")
    plot_system()

    while True:
        x0 = input_float("Начальное x: ")
        y0 = input_float("Начальное y: ")
        eps = input_float("Точность: ")

        try:
            x, y, it = newton_system(x0, y0, eps)
            break
        except ValueError as e:
            print(e)
            print("Попробуйте другие начальные значения.\n")

    print("\nРешение:")
    print("x =", x)
    print("y =", y)
    print("Итерации:", it)

    print("Проверка:")
    print(system1(x, y))


def main():
    while True:
        print("\nВыберите режим:")
        print("1. Решение одного нелинейного уравнения")
        print("2. Решение системы двух нелинейных уравнений")
        print("3. Выход")

        choice = input_int("Ваш выбор: ", 1, 3)

        if choice == 1:
            solve_equation()
        elif choice == 2:
            solve_system()
        else:
            break


if __name__ == "__main__":
    main()