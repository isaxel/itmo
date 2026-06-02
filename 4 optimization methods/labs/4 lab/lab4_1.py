import numpy as np

EPS = 1e-4
X0 = np.array([2.0, -3.0], dtype=float)

def f(x):
    x1, x2 = x
    return 2 * x1**2 + 2 * x1 * x2 + 3 * x2**2 + 10 * x1 - 10 * x2 + 35


def grad_f(x):
    x1, x2 = x
    return np.array([
        4 * x1 + 2 * x2 + 10,
        2 * x1 + 6 * x2 - 10
    ], dtype=float)


def hessian():
    return np.array([
        [4.0, 2.0],
        [2.0, 6.0]
    ], dtype=float)

import numpy as np

def golden_section_search(phi, a, b, eps=1e-4):
    gr = (np.sqrt(5) - 1) / 2

    c = b - gr * (b - a)
    d = a + gr * (b - a)

    fc = phi(c)
    fd = phi(d)

    while abs(b - a) > eps:
        if fc < fd:
            b = d
            d = c
            fd = fc
            c = b - gr * (b - a)
            fc = phi(c)
        else:
            a = c
            c = d
            fc = fd
            d = a + gr * (b - a)
            fd = phi(d)

    return (a + b) / 2


def coordinate_descent(x0, eps=1e-4, max_cycles=1000, search_bounds=(-20.0, 20.0)):
    x = x0.copy().astype(float)
    history = [x.copy()]

    a, b = search_bounds

    for _ in range(max_cycles):
        x_prev = x.copy()

        def phi1(x1):
            return f(np.array([x1, x[1]], dtype=float))

        x1_opt = golden_section_search(phi1, a, b, eps)
        x[0] = x1_opt
        history.append(x.copy())

        def phi2(x2):
            return f(np.array([x[0], x2], dtype=float))

        x2_opt = golden_section_search(phi2, a, b, eps)
        x[1] = x2_opt
        history.append(x.copy())
        if abs(f(x) - f(x_prev)) <= eps or np.linalg.norm(x - x_prev) <= eps:
            break

    return x, np.array(history)


def gradient_descent(x0, alpha0=0.1, eps=1e-4, max_iter=10000):
    x = x0.copy()
    history = [x.copy()]

    for _ in range(max_iter):
        g = grad_f(x)
        if np.linalg.norm(g) <= eps:
            break

        alpha = alpha0
        f_old = f(x)

        x_new = x - alpha * g

        while f(x_new) >= f_old:
            alpha /= 2.0
            if alpha < 1e-12:
                break
            x_new = x - alpha * g

        history.append(x_new.copy())

        if abs(f(x_new) - f_old) <= eps:
            x = x_new
            break

        x = x_new

    return x, np.array(history)


def steepest_descent(x0, eps=1e-4, max_iter=10000, search_bounds=(0.0, 1.0)):
    x = x0.copy().astype(float)
    history = [x.copy()]

    a, b = search_bounds

    for _ in range(max_iter):
        g = grad_f(x)

        if np.linalg.norm(g) <= eps:
            break

        def phi(h):
            return f(x - h * g)

        h = golden_section_search(phi, a, b, eps)
        x_new = x - h * g
        f_old = f(x)
        f_new = f(x_new)
        history.append(x_new.copy())

        if abs(f_new - f_old) <= eps:
            x = x_new
            break

        x = x_new

    return x, np.array(history)

def print_result(method_name, x_res, history):
    print(method_name)
    print(f"Количество приближений: {len(history)}")
    print(f"Результат: ({x_res[0]:.10f}, {x_res[1]:.10f})")
    print(f"Значение функции: {f(x_res):.10f}")
    print(f"Норма градиента: {np.linalg.norm(grad_f(x_res)):.10f}")

    print("\nПоследовательность приближений:")
    for k, x in enumerate(history):
        print(
            f"k = {k:2d} | "
            f"x = ({x[0]:10.6f}, {x[1]:10.6f}) | "
            f"f(x) = {f(x):12.6f}"
        )

x_cd, hist_cd = coordinate_descent(X0, eps=EPS)
x_gd, hist_gd = gradient_descent(X0, alpha0=0.2, eps=EPS)
x_sd, hist_sd = steepest_descent(X0, eps=EPS)

print_result("Метод покоординатного спуска", x_cd, hist_cd)
print_result("Метод градиентного спуска", x_gd, hist_gd)
print_result("Метод наискорейшего спуска", x_sd, hist_sd)