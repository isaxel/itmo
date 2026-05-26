import math
import os


def _normalize(raw: str) -> str:
    return raw.strip().replace(",", ".")


def _is_valid_float(s: str) -> bool:
    s = _normalize(s)
    if s.count(".") > 1:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def input_float(prompt: str) -> float:
    while True:
        raw = input(prompt)
        if _is_valid_float(raw):
            return float(_normalize(raw))
        print("  [!] Некорректный ввод. Введите вещественное число (пример: 1.5 или 1,5).")


def input_int_range(prompt: str, lo: int, hi: int) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            v = int(raw)
            if lo <= v <= hi:
                return v
            print(f"  [!] Введите число от {lo} до {hi}.")
        except ValueError:
            print("  [!] Некорректный ввод. Введите целое число.")


def input_positive_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            v = int(raw)
            if v > 0:
                return v
            print("  [!] Число должно быть положительным.")
        except ValueError:
            print("  [!] Некорректный ввод.")


def _parse_float_list(raw: str) -> list[float] | None:
    raw = raw.replace(";", " ")
    parts = raw.split()
    result = []
    for p in parts:
        if not _is_valid_float(p):
            return None
        result.append(float(_normalize(p)))
    return result if result else None


def input_float_list(prompt: str, min_count: int = 2) -> list[float]:
    while True:
        raw = input(prompt)
        lst = _parse_float_list(raw)
        if lst is None:
            print("  [!] Ошибка разбора. Вводите числа через пробел (пример: 1.1 2.2 3.3).")
            continue
        if len(lst) < min_count:
            print(f"  [!] Нужно минимум {min_count} числа.")
            continue
        return lst


def finite_differences(y: list[float]) -> list[list[float]]:
    n = len(y)
    delta = [list(y)]
    for k in range(1, n):
        prev = delta[k - 1]
        curr = [prev[i + 1] - prev[i] for i in range(len(prev) - 1)]
        delta.append(curr)
    return delta


def print_finite_diff_table(x: list[float], y: list[float],
                             delta: list[list[float]]) -> None:
    n = len(y)
    header = f"{'i':>3}  {'xi':>10}  {'yi':>12}"
    for k in range(1, n):
        header += f"  {'Δ^' + str(k) + 'yi':>14}"
    print(header)
    print("─" * (len(header) + 10))
    for i in range(n):
        row = f"{i:>3}  {x[i]:>10.4f}  {y[i]:>12.6f}"
        for k in range(1, n - i):
            if i < len(delta[k]):
                row += f"  {delta[k][i]:>14.7f}"
        print(row)


def lagrange(x: list[float], y: list[float], xp: float,
             verbose: bool = False) -> float:
    n = len(x)
    result = 0.0
    if verbose:
        print(f"\n  Формула: L(x) = Σ yᵢ · lᵢ(x)")
    for i in range(n):
        num = den = 1.0
        for j in range(n):
            if j != i:
                num *= (xp - x[j])
                den *= (x[i] - x[j])
        li = num / den
        contrib = y[i] * li
        if verbose:
            print(f"  l_{i}({xp}) = {li:+.8f},  "
                  f"y_{i}·l_{i} = {y[i]} · {li:+.8f} = {contrib:+.8f}")
        result += contrib
    return result


def newton_forward(y: list[float], delta: list[list[float]],
                   x0: float, h: float, xp: float,
                   verbose: bool = False) -> float:
    t = (xp - x0) / h
    n = len(y) - 1
    if verbose:
        print(f"\n  Используется 1-я формула Ньютона (интерполирование вперёд)")
        print(f"  t = ({xp} − {x0}) / {h} = {t:.6f}")
        print(f"  N(x) = y₀ + t·Δy₀ + t(t-1)/2!·Δ²y₀ + …")

    result = y[0]
    product = 1.0
    if verbose:
        print(f"\n  Слагаемое 0: y₀ = {y[0]:.6f}")
    for k in range(1, n + 1):
        if k > len(delta[k]) + k - 1 or not delta[k]:
            break
        product *= (t - (k - 1))
        coeff = product / math.factorial(k)
        term = coeff * delta[k][0]
        result += term
        if verbose:
            print(f"  Слагаемое {k}: коэф={coeff:+.7f}, "
                  f"Δ^{k}y₀={delta[k][0]:+.7f}, член={term:+.8f}")
    return result


def newton_backward(y: list[float], delta: list[list[float]],
                    xn: float, h: float, xp: float,
                    verbose: bool = False) -> float:
    t = (xp - xn) / h
    n = len(y) - 1
    if verbose:
        print(f"\n  Используется 2-я формула Ньютона (интерполирование назад)")
        print(f"  t = ({xp} − {xn}) / {h} = {t:.6f}")
        print(f"  N(x) = yₙ + t·Δyₙ₋₁ + t(t+1)/2!·Δ²yₙ₋₂ + …")

    result = y[-1]
    product = 1.0
    if verbose:
        print(f"\n  Слагаемое 0: yₙ = {y[-1]:.6f}")
    for k in range(1, n + 1):
        if not delta[k]:
            break
        product *= (t + (k - 1))
        coeff = product / math.factorial(k)
        term = coeff * delta[k][-1]
        result += term
        if verbose:
            print(f"  Слагаемое {k}: коэф={coeff:+.7f}, "
                  f"Δ^{k}yₙ₋{k}={delta[k][-1]:+.7f}, член={term:+.8f}")
    return result


def newton_finite(x: list[float], y: list[float], xp: float,
                  verbose: bool = False) -> tuple[float, str]:
    h_vals = [round(x[i + 1] - x[i], 10) for i in range(len(x) - 1)]
    h = h_vals[0]
    equal = all(abs(hv - h) < 1e-8 for hv in h_vals)
    if not equal:
        raise ValueError("Формула Ньютона с конечными разностями требует "
                         "равноотстоящих узлов.")
    delta = finite_differences(y)
    mid = (x[0] + x[-1]) / 2
    if xp <= mid:
        if verbose:
            print(f"  xp={xp} ≤ середина={mid:.4f} → левая часть")
        val = newton_forward(y, delta, x[0], h, xp, verbose)
        return val, "forward"
    else:
        if verbose:
            print(f"  xp={xp} > середина={mid:.4f} → правая часть")
        val = newton_backward(y, delta, x[-1], h, xp, verbose)
        return val, "backward"


def gauss_forward(y: list[float], delta: list[list[float]],
                  center_idx: int, h: float, xp: float,
                  x_nodes: list[float], verbose: bool = False) -> float:
    a = x_nodes[center_idx]
    t = (xp - a) / h
    if verbose:
        print(f"\n  1-я формула Гаусса (x > a)")
        print(f"  Центральный узел a = x[{center_idx}] = {a}")
        print(f"  t = ({xp} − {a}) / {h} = {t:.6f}")

    result = y[center_idx]
    if verbose:
        print(f"  Слагаемое 0: y₀ = {y[center_idx]:.6f}")

    ci = center_idx
    # k=1: t · Δy₀
    if ci < len(delta[1]):
        term = t * delta[1][ci]
        result += term
        if verbose:
            print(f"  Слагаемое 1: t·Δy₀ = {t:.6f}·{delta[1][ci]:.6f} = {term:.8f}")
    # k=2: t(t-1)/2 · Δ²y₋₁
    idx2 = ci - 1
    if 0 <= idx2 < len(delta[2]):
        c = t * (t - 1) / 2
        term = c * delta[2][idx2]
        result += term
        if verbose:
            print(f"  Слагаемое 2: t(t-1)/2·Δ²y_{{-1}} = {c:.6f}·{delta[2][idx2]:.6f} = {term:.8f}")
    # k=3: (t+1)t(t-1)/6 · Δ³y₋₁
    idx3 = ci - 1
    if 0 <= idx3 < len(delta[3]):
        c = (t + 1) * t * (t - 1) / 6
        term = c * delta[3][idx3]
        result += term
        if verbose:
            print(f"  Слагаемое 3: (t+1)t(t-1)/6·Δ³y_{{-1}} = {c:.6f}·{delta[3][idx3]:.6f} = {term:.8f}")
    # k=4: (t+1)t(t-1)(t-2)/24 · Δ⁴y₋₂
    idx4 = ci - 2
    if 0 <= idx4 < len(delta[4]):
        c = (t + 1) * t * (t - 1) * (t - 2) / 24
        term = c * delta[4][idx4]
        result += term
        if verbose:
            print(f"  Слагаемое 4: (t+1)t(t-1)(t-2)/24·Δ⁴y_{{-2}} = {c:.6f}·{delta[4][idx4]:.6f} = {term:.8f}")
    # k=5
    idx5 = ci - 2
    if len(delta) > 5 and 0 <= idx5 < len(delta[5]):
        c = (t + 2) * (t + 1) * t * (t - 1) * (t - 2) / 120
        term = c * delta[5][idx5]
        result += term
        if verbose:
            print(f"  Слагаемое 5: ...·Δ⁵y_{{-2}} = {c:.6f}·{delta[5][idx5]:.6f} = {term:.8f}")
    return result


def gauss_backward(y: list[float], delta: list[list[float]],
                   center_idx: int, h: float, xp: float,
                   x_nodes: list[float], verbose: bool = False) -> float:
    a = x_nodes[center_idx]
    t = (xp - a) / h
    if verbose:
        print(f"\n  2-я формула Гаусса (x < a)")
        print(f"  Центральный узел a = x[{center_idx}] = {a}")
        print(f"  t = ({xp} − {a}) / {h} = {t:.6f}")

    result = y[center_idx]
    if verbose:
        print(f"  Слагаемое 0: y₀ = {y[center_idx]:.6f}")

    ci = center_idx
    # k=1: t · Δy₋₁
    idx1 = ci - 1
    if 0 <= idx1 < len(delta[1]):
        term = t * delta[1][idx1]
        result += term
        if verbose:
            print(f"  Слагаемое 1: t·Δy_{{-1}} = {t:.6f}·{delta[1][idx1]:.6f} = {term:.8f}")
    # k=2: t(t+1)/2 · Δ²y₋₁
    idx2 = ci - 1
    if 0 <= idx2 < len(delta[2]):
        c = t * (t + 1) / 2
        term = c * delta[2][idx2]
        result += term
        if verbose:
            print(f"  Слагаемое 2: t(t+1)/2·Δ²y_{{-1}} = {c:.6f}·{delta[2][idx2]:.6f} = {term:.8f}")
    # k=3: (t+1)t(t-1)/6 · Δ³y₋₂
    idx3 = ci - 2
    if 0 <= idx3 < len(delta[3]):
        c = (t + 1) * t * (t - 1) / 6
        term = c * delta[3][idx3]
        result += term
        if verbose:
            print(f"  Слагаемое 3: (t+1)t(t-1)/6·Δ³y_{{-2}} = {c:.6f}·{delta[3][idx3]:.6f} = {term:.8f}")
    # k=4: (t+2)(t+1)t(t-1)/24 · Δ⁴y₋₂
    idx4 = ci - 2
    if 0 <= idx4 < len(delta[4]):
        c = (t + 2) * (t + 1) * t * (t - 1) / 24
        term = c * delta[4][idx4]
        result += term
        if verbose:
            print(f"  Слагаемое 4: (t+2)(t+1)t(t-1)/24·Δ⁴y_{{-2}} = {c:.6f}·{delta[4][idx4]:.6f} = {term:.8f}")
    # k=5
    idx5 = ci - 3
    if len(delta) > 5 and 0 <= idx5 < len(delta[5]):
        c = (t + 2) * (t + 1) * t * (t - 1) * (t - 2) / 120
        term = c * delta[5][idx5]
        result += term
        if verbose:
            print(f"  Слагаемое 5: ...·Δ⁵y_{{-3}} = {c:.6f}·{delta[5][idx5]:.6f} = {term:.8f}")
    return result


def gauss_auto(x: list[float], y: list[float], xp: float,
               verbose: bool = False) -> tuple[float, float, str, str]:
    h_vals = [round(x[i + 1] - x[i], 10) for i in range(len(x) - 1)]
    h = h_vals[0]
    equal = all(abs(hv - h) < 1e-8 for hv in h_vals)
    if not equal:
        raise ValueError("Формулы Гаусса требуют равноотстоящих узлов.")

    delta = finite_differences(y)

    dists = [abs(xi - xp) for xi in x]
    ci = dists.index(min(dists))
    a = x[ci]
    t = (xp - a) / h

    if verbose:
        print(f"\n  Ближайший узел к xp={xp}: x[{ci}]={a}, t={t:.6f}")

    if t >= 0:
        if ci == 0:
            ci_f = 1
        else:
            ci_f = ci
        f1_val = gauss_forward(y, delta, ci_f, h, xp, x, verbose)
        f1_name = f"1-я (центр x[{ci_f}]={x[ci_f]}, t={(xp-x[ci_f])/h:.4f})"
        ci_b = ci_f
        f2_val = gauss_backward(y, delta, ci_b, h, xp, x, verbose)
        f2_name = f"2-я (центр x[{ci_b}]={x[ci_b]}, t={(xp-x[ci_b])/h:.4f})"
    else:
        if ci == len(x) - 1:
            ci_b = len(x) - 2
        else:
            ci_b = ci
        f2_val = gauss_backward(y, delta, ci_b, h, xp, x, verbose)
        f2_name = f"2-я (центр x[{ci_b}]={x[ci_b]}, t={(xp-x[ci_b])/h:.4f})"
        ci_f = ci_b
        f1_val = gauss_forward(y, delta, ci_f, h, xp, x, verbose)
        f1_name = f"1-я (центр x[{ci_f}]={x[ci_f]}, t={(xp-x[ci_f])/h:.4f})"

    return f1_val, f2_val, f1_name, f2_name


BUILTIN_FUNCTIONS = {
    "1": ("sin(x)",   math.sin),
    "2": ("cos(x)",   math.cos),
    "3": ("exp(x)",   math.exp),
    "4": ("ln(x)",    math.log),
    "5": ("x²",       lambda x: x ** 2),
    "6": ("√x",       math.sqrt),
}

TEST_FILES = {
    "test1.txt": (
        "# Тест 1: равноотстоящие, 5 узлов\n"
        "0.1 1.25\n0.2 2.38\n0.3 3.79\n0.4 5.44\n0.5 7.14\n"
    ),
    "test2.txt": (
        "# Тест 2: Таблица 1.3 варианта 3\n"
        "1.10 0.2234\n1.25 1.2438\n1.40 2.2644\n"
        "1.55 3.2984\n1.70 4.3222\n1.85 5.3516\n2.00 6.3867\n"
    ),
    "test3.txt": (
        "# Тест 3: sin(x), 6 узлов\n"
        "0.0 0.0\n0.5 0.4794\n1.0 0.8415\n"
        "1.5 0.9975\n2.0 0.9093\n2.5 0.5985\n"
    ),
}


def _ensure_test_files() -> None:
    for fname, content in TEST_FILES.items():
        if not os.path.exists(fname):
            with open(fname, "w", encoding="utf-8") as f:
                f.write(content)


def load_from_keyboard() -> tuple[list[float], list[float]]:
    print("\n  Введите количество узлов:")
    n = input_positive_int("  n = ")
    print(f"  Введите {n} пар (xi yi) — по одной в строке, числа через пробел:")
    x_list, y_list = [], []
    for i in range(n):
        while True:
            raw = input(f"  Пара {i + 1}: ")
            parts = _parse_float_list(raw)
            if parts and len(parts) == 2:
                x_list.append(parts[0])
                y_list.append(parts[1])
                break
            print("  [!] Введите ровно два числа через пробел.")
    return x_list, y_list


def load_from_file() -> tuple[list[float], list[float]] | None:
    _ensure_test_files()
    print("\n  Доступные файлы:")
    for fname in TEST_FILES:
        print(f"    {fname}")
    while True:
        fname = input("  Имя файла (или Enter для отмены): ").strip()
        if not fname:
            return None
        if not os.path.exists(fname):
            print(f"  [!] Файл '{fname}' не найден.")
            continue
        x_list, y_list = [], []
        try:
            with open(fname, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = _parse_float_list(line)
                    if parts and len(parts) >= 2:
                        x_list.append(parts[0])
                        y_list.append(parts[1])
        except Exception as e:
            print(f"  [!] Ошибка чтения файла: {e}")
            continue
        if len(x_list) < 2:
            print("  [!] В файле менее 2 узлов.")
            continue
        print(f"  Загружено {len(x_list)} узлов из '{fname}'.")
        return x_list, y_list


def load_from_function() -> tuple[list[float], list[float]]:
    print("\n  Выберите функцию:")
    for k, (name, _) in BUILTIN_FUNCTIONS.items():
        print(f"    {k}. {name}")
    choice = str(input_int_range("  Номер: ", 1, len(BUILTIN_FUNCTIONS)))
    name, func = BUILTIN_FUNCTIONS[choice]
    print(f"  Функция: {name}")
    a = input_float("  Левая граница a = ")
    b = input_float("  Правая граница b = ")
    if b <= a:
        print("  [!] b должно быть > a. Меняю местами.")
        a, b = b, a
    n = input_positive_int("  Количество точек (≥ 2): ")
    if n < 2:
        n = 2
    step = (b - a) / (n - 1)
    x_list, y_list = [], []
    for i in range(n):
        xi = a + i * step
        try:
            yi = func(xi)
            x_list.append(xi)
            y_list.append(yi)
        except Exception:
            print(f"  [!] Функция не определена в x={xi:.4f}, пропуск.")
    return x_list, y_list


def get_data() -> tuple[list[float], list[float]] | None:
    print("\nИСТОЧНИК ДАННЫХ")
    print("1. Ввод с клавиатуры")
    print("2. Загрузка из файла")
    print("3. Встроенная функция")
    choice = input_int_range("  Выбор: ", 1, 3)
    if choice == 1:
        return load_from_keyboard()
    elif choice == 2:
        return load_from_file()
    else:
        return load_from_function()


def _check_equal_spacing(x: list[float]) -> tuple[bool, float]:
    h_vals = [x[i + 1] - x[i] for i in range(len(x) - 1)]
    h = h_vals[0]
    return all(abs(hv - h) < 1e-8 for hv in h_vals), h


def _print_nodes(x, y):
    print("\n  Узлы интерполяции:")
    print(f"  {'i':>3}  {'x':>10}  {'y':>14}")
    print("  " + "─" * 30)
    for i, (xi, yi) in enumerate(zip(x, y)):
        print(f"  {i:>3}  {xi:>10.6f}  {yi:>14.8f}")


def run_lagrange(x, y):
    print("  МЕТОД ЛАГРАНЖА")
    _print_nodes(x, y)
    xp = input_float("\n  Введите x для интерполяции: ")
    result = lagrange(x, y, xp, verbose=True)
    print(f"\n  ► L({xp}) = {result:.8f}")


def run_newton_finite(x, y):
    print("  МЕТОД НЬЮТОНА (конечные разности)")
    equal, h = _check_equal_spacing(x)
    if not equal:
        print("  [!] Узлы неравноотстоящие — метод неприменим.")
        return
    print(f"  Шаг h = {h:.6f}")
    _print_nodes(x, y)

    delta = finite_differences(y)
    print("\n  Таблица конечных разностей:")
    print_finite_diff_table(x, y, delta)

    xp = input_float("\n  Введите x для интерполяции: ")
    mid = (x[0] + x[-1]) / 2
    print(f"\n  Середина таблицы: {mid:.4f}")

    val_f, which = newton_finite(x, y, xp, verbose=True)
    formula = "1-я (вперёд)" if which == "forward" else "2-я (назад)"
    print(f"\n  ► Использована {formula}")
    print(f"  ► N({xp}) = {val_f:.8f}")

    # Показываем обе для сравнения
    if which == "forward":
        val_b = newton_backward(y, delta, x[-1], h, xp, verbose=False)
        print(f"  (2-я формула для сравнения: {val_b:.8f})")
    else:
        val_f2 = newton_forward(y, delta, x[0], h, xp, verbose=False)
        print(f"  (1-я формула для сравнения: {val_f2:.8f})")


def run_gauss(x, y):
    print("  МЕТОД ГАУССА")
    equal, h = _check_equal_spacing(x)
    if not equal:
        print("  [!] Узлы неравноотстоящие — метод неприменим.")
        return
    print(f"  Шаг h = {h:.6f}")
    _print_nodes(x, y)

    delta = finite_differences(y)
    print("\n  Таблица конечных разностей:")
    print_finite_diff_table(x, y, delta)

    xp = input_float("\n  Введите x для интерполяции: ")

    f1_val, f2_val, f1_name, f2_name = gauss_auto(x, y, xp, verbose=True)

    print(f"\n  ► 1-я формула Гаусса ({f1_name}): {f1_val:.8f}")
    print(f"  ► 2-я формула Гаусса ({f2_name}): {f2_val:.8f}")

    lag = lagrange(x, y, xp)
    print(f"\n  Для сравнения Лагранж: {lag:.8f}")


def run_comparison(x, y):
    print("  СРАВНЕНИЕ МЕТОДОВ")
    _print_nodes(x, y)
    xp = input_float("\n  Введите x для интерполяции: ")

    results = {}
    results["Лагранж"] = lagrange(x, y, xp)

    equal, h = _check_equal_spacing(x)
    if equal:
        delta = finite_differences(y)
        val_f = newton_forward(y, delta, x[0], h, xp)
        results["Ньютон 1-я"] = val_f
        val_b = newton_backward(y, delta, x[-1], h, xp)
        results["Ньютон 2-я"] = val_b
        f1, f2, _, _ = gauss_auto(x, y, xp)
        results["Гаусс 1-я"] = f1
        results["Гаусс 2-я"] = f2
    else:
        print("  (Узлы неравноотстоящие: Ньютон конечн. и Гаусс недоступны)")

    print(f"\n  Результаты для x = {xp}:")
    print(f"  {'Метод':<20} {'Значение':>14}")
    print("  " + "─" * 36)
    for name, val in results.items():
        print(f"  {name:<20} {val:>14.8f}")



MENU_METHODS = [
    ("Многочлен Лагранжа",                         run_lagrange),
    ("Ньютон (конечные разности, 1-я и 2-я)",       run_newton_finite),
    ("Гаусс (1-я и 2-я формулы)",                  run_gauss),
    ("Сравнение всех методов",                     run_comparison),
]


def print_main_menu():
    print("Лабораторная работа №5: Интерполяция функции")
    print("Методы:")
    for i, (name, _) in enumerate(MENU_METHODS, 1):
        print(f"{i}. {name:<48}")
    print("0. Выход")


def main():
    _ensure_test_files()
    x_data: list[float] | None = None
    y_data: list[float] | None = None

    while True:
        print_main_menu()
        if x_data is not None:
            print(f"  [Текущий набор: {len(x_data)} узлов, "
                  f"x ∈ [{x_data[0]:.4f}, {x_data[-1]:.4f}]]")
        print("\n  Сначала загрузите данные (или используйте загруженные).")
        print("  d — загрузить/изменить данные")

        raw = input("  Выбор [0-4 / d]: ").strip().lower()

        if raw == "0":
            break

        if raw == "d" or x_data is None:
            if raw != "d":
                print("  [!] Данные не загружены. Загрузите их сначала.")
            result = get_data()
            if result is None:
                print("  Загрузка отменена.")
                continue
            x_data, y_data = result
            if len(x_data) < 2:
                print("  [!] Нужно минимум 2 узла.")
                x_data = y_data = None
            continue

        try:
            choice = int(raw)
        except ValueError:
            print("  [!] Неверный ввод.")
            continue

        if choice < 1 or choice > len(MENU_METHODS):
            print(f"  [!] Введите число от 0 до {len(MENU_METHODS)} или 'd'.")
            continue

        name, func = MENU_METHODS[choice - 1]
        print(f"\n  → {name}")
        try:
            func(x_data, y_data)
        except Exception as e:
            print(f"\n  [!] Ошибка: {e}")

        input("\n  Нажмите Enter для возврата в меню...")


if __name__ == "__main__":
    main()