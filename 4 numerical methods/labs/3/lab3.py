import math


def get_float(prompt):
    while True:
        val = input(prompt).strip().replace(',', '.')
        try:
            return float(val)
        except ValueError:
            print("Ошибка: введите число.")


def get_int(prompt, valid_range=None):
    while True:
        val = input(prompt).strip()
        try:
            num = int(val)
            if valid_range and num not in valid_range:
                print(f"Ошибка: выберите вариант из {valid_range}.")
                continue
            return num
        except ValueError:
            print("Ошибка: введите целое число.")


class Integrands:
    @staticmethod
    def f1(x):
        return x ** 2

    @staticmethod
    def f1_exact(a, b):
        return (b ** 3 - a ** 3) / 3

    @staticmethod
    def f2(x):
        if x == 0: raise ValueError("Деление на ноль")
        return 1 / x

    @staticmethod
    def f2_exact(a, b):
        return math.log(abs(b)) - math.log(abs(a))

    @staticmethod
    def f3(x):
        if x <= 0: raise ValueError("Корень из отрицательного числа или нуля")
        return 1 / math.sqrt(x)

    @staticmethod
    def f3_exact(a, b):
        return 2 * math.sqrt(b) - 2 * math.sqrt(a)

    @staticmethod
    def f4(x):
        d = 1 - x ** 2
        if d <= 0: raise ValueError("Выход за область определения f(x)")
        return 1 / math.sqrt(d)

    @staticmethod
    def f4_exact(a, b):
        return math.asin(b) - math.asin(a)


FUNCTIONS = [
    {"name": "f(x) = x^2", "f": Integrands.f1, "exact": Integrands.f1_exact,
     "sings": [], "domain": (-float('inf'), float('inf')), "conv": True},
    {"name": "f(x) = 1/x (Разрыв в 0, расходится)", "f": Integrands.f2, "exact": Integrands.f2_exact,
     "sings": [0], "domain": (-float('inf'), float('inf')), "conv": False},
    {"name": "f(x) = 1/sqrt(x) (Разрыв в 0, сходится)", "f": Integrands.f3, "exact": Integrands.f3_exact,
     "sings": [0], "domain": (0, float('inf')), "conv": True},
    {"name": "f(x) = 1/sqrt(1-x^2) (Разрывы -1, 1, сходится)", "f": Integrands.f4, "exact": Integrands.f4_exact,
     "sings": [-1, 1], "domain": (-1, 1), "conv": True}
]


class Methods:
    @staticmethod
    def left_rect(f, a, b, n):
        h = (b - a) / n
        return h * sum(f(a + i * h) for i in range(n))

    @staticmethod
    def right_rect(f, a, b, n):
        h = (b - a) / n
        return h * sum(f(a + (i + 1) * h) for i in range(n))

    @staticmethod
    def mid_rect(f, a, b, n):
        h = (b - a) / n
        return h * sum(f(a + (i + 0.5) * h) for i in range(n))

    @staticmethod
    def trapezoid(f, a, b, n):
        h = (b - a) / n
        return h * (0.5 * (f(a) + f(b)) + sum(f(a + i * h) for i in range(1, n)))

    @staticmethod
    def simpson(f, a, b, n):
        if n % 2 != 0: n += 1
        h = (b - a) / n
        s1 = sum(f(a + i * h) for i in range(1, n, 2))
        s2 = sum(f(a + i * h) for i in range(2, n, 2))
        return (h / 3) * (f(a) + f(b) + 4 * s1 + 2 * s2)


def solve_with_runge(method, f, a, b, eps, p):
    n = 4
    try:
        i_old = method(f, a, b, n)
        while n < 1_000_000:
            n *= 2
            i_new = method(f, a, b, n)
            if abs(i_new - i_old) / (2 ** p - 1) <= eps:
                return i_new, n
            i_old = i_new
        return i_old, n
    except (ValueError, ZeroDivisionError):
        return None, n


def get_safe_intervals(a, b, sings, sigma=1e-7):
    points = sorted(list(set([a, b] + [s for s in sings if a < s < b])))
    intervals = []
    for i in range(len(points) - 1):
        s, e = points[i], points[i + 1]
        if s in sings: s += sigma
        if e in sings: e -= sigma
        if s < e: intervals.append((s, e))
    return intervals


def main():
    while True:
        print("\n")
        for i, fn in enumerate(FUNCTIONS, 1):
            print(f"{i}. {fn['name']}")
        print("0. Завершить программу")

        f_idx = get_int("Выберите функцию: ", list(range(5)))
        if f_idx == 0: break
        fn_obj = FUNCTIONS[f_idx - 1]

        a = get_float("Введите нижний предел a: ")
        b = get_float("Введите верхний предел b: ")
        if a > b:
            a, b = b, a
            print("Внимание: границы перевернуты.")

        d_min, d_max = fn_obj["domain"]
        if a < d_min or b > d_max:
            print(f"Ошибка: Функция определена только в интервале [{d_min}, {d_max}].")
            continue

        eps = get_float("Введите точность: ")
        print("\nВыберите метод:")
        print("1. Левые прямоугольники")
        print("2. Правые прямоугольники")
        print("3. Средние прямоугольники")
        print("4. Трапеции")
        print("5. Симпсона")
        m_idx = get_int("Ваш выбор: ", [1, 2, 3, 4, 5])

        m_map = {1: (Methods.left_rect, 1, "Левые"), 2: (Methods.right_rect, 1, "Правые"),
                 3: (Methods.mid_rect, 2, "Средние"), 4: (Methods.trapezoid, 2, "Трапеции"),
                 5: (Methods.simpson, 4, "Симпсон")}
        method_func, p_order, m_name = m_map[m_idx]

        if any(a <= s <= b for s in fn_obj["sings"]) and not fn_obj["conv"]:
            print("Результат: Интеграл расходится.")
            continue

        intervals = get_safe_intervals(a, b, fn_obj["sings"])
        total_integral, max_n = 0, 0
        error_occured = False

        for start, end in intervals:
            res, n_final = solve_with_runge(method_func, fn_obj["f"], start, end, eps, p_order)
            if res is None:
                error_occured = True
                break
            total_integral += res
            max_n = max(max_n, n_final)

        if error_occured:
            print("Ошибка: Функция не определена в некоторых точках интервала.")
        else:
            exact = sum(fn_obj["exact"](u, v) for u, v in intervals)
            print(f"\nМетод: {m_name}\nЗначение: {total_integral:.8f}\nРазбиения (n): {max_n}")
            print(f"Точное: {exact:.8f}\nПогрешность: {abs(exact - total_integral):.2e}")


if __name__ == "__main__":
    main()