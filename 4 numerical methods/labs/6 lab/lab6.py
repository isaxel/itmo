import math
import matplotlib.pyplot as plt
import numpy as np

equations = {
    1: {
        "name": "y' = y",
        "f": lambda x, y: y,
        "exact": lambda x, x0, y0: y0 * math.exp(x - x0)
    },
    2: {
        "name": "y' = 2*x*y",
        "f": lambda x, y: 2 * x * y,
        "exact": lambda x, x0, y0: y0 * math.exp(x**2 - x0**2)
    },
    3: {
        "name": "y' = -2*x*y",
        "f": lambda x, y: -2 * x * y,
        "exact": lambda x, x0, y0: y0 * math.exp(-(x**2 - x0**2))
    }
}


def euler_method(f, x0, y0, xn, h):
    n = int(round((xn - x0) / h))
    x = [x0 + i * h for i in range(n + 1)]
    y = [0.0] * (n + 1)
    y[0] = y0
    for i in range(n):
        y[i + 1] = y[i] + h * f(x[i], y[i])
    return x, y


def runge_kutta4_method(f, x0, y0, xn, h):
    n = int(round((xn - x0) / h))
    x = [x0 + i * h for i in range(n + 1)]
    y = [0.0] * (n + 1)
    y[0] = y0
    for i in range(n):
        k1 = h * f(x[i], y[i])
        k2 = h * f(x[i] + h / 2, y[i] + k1 / 2)
        k3 = h * f(x[i] + h / 2, y[i] + k2 / 2)
        k4 = h * f(x[i] + h, y[i] + k3)
        y[i + 1] = y[i] + (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return x, y


def milne_method(f, x0, y0, xn, h):
    n = int(round((xn - x0) / h))
    if n < 4:
        raise ValueError("Методу Милна нужно минимум 4 шага. Увеличьте интервал или уменьшите шаг.")
    x = [x0 + i * h for i in range(n + 1)]
    y = [0.0] * (n + 1)
    y[0] = y0

    for i in range(3):
        xi = x[i]
        yi = y[i]
        k1 = h * f(xi, yi)
        k2 = h * f(xi + h / 2, yi + k1 / 2)
        k3 = h * f(xi + h / 2, yi + k2 / 2)
        k4 = h * f(xi + h, yi + k3)
        y[i + 1] = yi + (k1 + 2 * k2 + 2 * k3 + k4) / 6

    for idx in range(4, n + 1):
        y_pred = (y[idx - 4] +
                  (4 * h / 3) * (2 * f(x[idx - 3], y[idx - 3]) -
                                 f(x[idx - 2], y[idx - 2]) +
                                 2 * f(x[idx - 1], y[idx - 1])))
        f_pred = f(x[idx], y_pred)
        y_corr = (y[idx - 2] +
                  (h / 3) * (f(x[idx - 2], y[idx - 2]) +
                             4 * f(x[idx - 1], y[idx - 1]) +
                             f_pred))
        y[idx] = y_corr

    return x, y


def runge_rule_error(method, f, x0, y0, xn, h, p):
    _, y_h = method(f, x0, y0, xn, h)
    _, y_h2 = method(f, x0, y0, xn, h / 2)
    error = abs(y_h[-1] - y_h2[-1]) / (2**p - 1)
    return error


def exact_max_error(y_approx, exact_func, x_list, x0, y0):
    exact_vals = [exact_func(x, x0, y0) for x in x_list]
    return max(abs(ya - ye) for ya, ye in zip(y_approx, exact_vals))


def input_float(prompt):
    while True:
        s = input(prompt).strip()
        if not s:
            continue
        s_dot = s.replace(',', '.')
        try:
            val = float(s_dot)
            return val
        except ValueError:
            print("Ошибка: введите число (используйте точку или запятую).")


def print_table(x, y, title=""):
    print(f"\n{title}")
    print(f"{'x':>10} {'y':>20}")
    for xi, yi in zip(x, y):
        print(f"{xi:10.6f} {yi:20.10f}")


def plot_solution(x, y_approx, exact_func, x0, y0, method_name, eq_name):
    x_fine = np.linspace(x[0], x[-1], 200)
    y_exact = [exact_func(xi, x0, y0) for xi in x_fine]

    plt.figure(figsize=(8, 5))
    plt.plot(x_fine, y_exact, 'b-', label='Точное решение')
    plt.plot(x, y_approx, 'ro--', markersize=4, label=f'{method_name} (приближённое)')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title(f'{method_name} – {eq_name}')
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    while True:
        print("1. Метод Эйлера")
        print("2. Метод Рунге-Кутты 4-го порядка")
        print("3. Метод Милна")
        print("4. Выход")
        choice = input("Выберите (1-4): ").strip()
        if choice == '4':
            break

        if choice not in ('1', '2', '3'):
            print("Неверный выбор. Пожалуйста, введите 1, 2, 3 или 4.")
            continue

        print("\nДоступные ОДУ:")
        for k, v in equations.items():
            print(f"  {k}. {v['name']}")
        eq_choice = input("Выберите ОДУ (1-3): ").strip()
        if eq_choice not in ('1', '2', '3'):
            print("Неверный номер ОДУ.")
            continue
        eq = equations[int(eq_choice)]
        f = eq['f']
        exact = eq['exact']

        print("\nВведите параметры задачи")
        x0 = input_float("x0 = ")
        y0 = input_float("y0 = ")
        xn = input_float("xn (конец интервала) = ")
        if xn <= x0:
            print("xn должно быть больше x0. Повторите выбор метода.")
            continue
        h = input_float("Шаг h (>0) = ")
        if h <= 0:
            print("Шаг должен быть положительным.")
            continue

        n = int(round((xn - x0) / h))
        h_actual = (xn - x0) / n
        if abs(h_actual - h) > 1e-12:
            print(f"Шаг скорректирован на {h_actual:.10f} для точного попадания в интервал.")
        h = h_actual

        eps = input_float("Требуемая точность ε (для правила Рунге) = ")

        method_name = ""
        method_func = None
        order = None
        if choice == '1':
            method_name = "Метод Эйлера"
            method_func = euler_method
            order = 1
        elif choice == '2':
            method_name = "Метод Рунге-Кутты 4"
            method_func = runge_kutta4_method
            order = 4
        else:
            method_name = "Метод Милна"
            method_func = milne_method
            order = 4

        try:
            x_vals, y_vals = method_func(f, x0, y0, xn, h)

            print_table(x_vals, y_vals, title=f"Решение методом {method_name}")

            err = runge_rule_error(method_func, f, x0, y0, xn, h, order)
            print(f"\nОценка глобальной погрешности в x = {xn} (правило Рунге): {err:.2e}")
            if err <= eps:
                print("Требуемая точность достигнута.")
            else:
                print(f"Точность НЕ достигнута (требуется ε={eps:.2e}). Попробуйте меньший шаг h.")

            plot_solution(x_vals, y_vals, exact, x0, y0, method_name, eq['name'])

            input("\nНажмите Enter, чтобы вернуться в главное меню")

        except Exception as e:
            print(f"Ошибка при вычислениях: {e}")
            input("\nНажмите Enter, чтобы продолжить")


if __name__ == "__main__":
    main()