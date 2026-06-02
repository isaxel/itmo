# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt


EPS = 1e-4


def f(x):
    return np.sqrt(1 + x**2) + np.exp(-2*x)


def df(x):
    return x / np.sqrt(1 + x**2) - 2*np.exp(-2*x)


def hermite_coefficients(x0, x1):
    delta = x1 - x0

    y0 = f(x0)
    y1 = f(x1)
    dy0 = df(x0)
    dy1 = df(x1)

    A = y0
    B = dy0 + 2 * y0 / delta
    C = y1
    D = -dy1 + 2 * y1 / delta

    return A, B, C, D


def H_value(x, x0, x1, A, B, C, D):
    delta = x1 - x0

    H0 = (A + B * (x - x0)) * (x1 - x) ** 2 / delta ** 2
    H1 = (C + D * (x1 - x)) * (x - x0) ** 2 / delta ** 2

    return H0 + H1


def hermite_power_coefficients(x0, x1, A, B, C, D):
    delta = x1 - x0

    alpha3 = (B - D) / delta**2

    alpha2 = (
        A - B * x0 - 2 * B * x1
        + C + D * x1 + 2 * D * x0
    ) / delta**2

    alpha1 = (
        (-2 * A + 2 * B * x0 + B * x1) * x1
        + (-2 * C - 2 * D * x1 - D * x0) * x0
    ) / delta**2

    alpha0 = (
        (A - B * x0) * x1**2
        + (C + D * x1) * x0**2
    ) / delta**2

    return alpha3, alpha2, alpha1, alpha0


def hermite_minimum(x0, x1):
    A, B, C, D = hermite_coefficients(x0, x1)
    alpha3, alpha2, alpha1, alpha0 = hermite_power_coefficients(x0, x1, A, B, C, D)

    roots = []

    if abs(alpha3) < 1e-14:
        if abs(alpha2) > 1e-14:
            roots.append(-alpha1 / (2 * alpha2))
    else:
        discriminant = alpha2**2 - 3 * alpha1 * alpha3

        if discriminant >= 0:
            r1 = (-alpha2 + np.sqrt(discriminant)) / (3 * alpha3)
            r2 = (-alpha2 - np.sqrt(discriminant)) / (3 * alpha3)
            roots.extend([r1, r2])

    candidates = [r for r in roots if x0 < r < x1]

    if not candidates:
        candidates = [x0, x1]

    xm = min(candidates, key=lambda x: H_value(x, x0, x1, A, B, C, D))

    return xm, A, B, C, D, alpha3, alpha2, alpha1, alpha0


def cubic_interpolation(x0=0.0, x1=1.0, eps=EPS, max_iter=100):
    path = []
    iteration = 1

    while iteration <= max_iter:
        xm, A, B, C, D, alpha3, alpha2, alpha1, alpha0 = hermite_minimum(x0, x1)
        derivative_value = df(xm)

        path.append([
            iteration,
            x0,
            x1,
            xm,
            derivative_value,
            f(xm),
            A,
            B,
            C,
            D
        ])

        xs = np.linspace(0, 1, 500)
        mask = (xs >= x0) & (xs <= x1)

        plt.figure(figsize=(8, 5))
        plt.plot(xs, f(xs), linewidth=2, label="Исходная функция f(x)")
        plt.plot(
            xs[mask],
            H_value(xs[mask], x0, x1, A, B, C, D),
            "--",
            linewidth=2,
            label="Кубическая интерполяция"
        )
        plt.scatter(xm, f(xm), s=50, label=f"xm = {xm:.4f}")
        plt.grid(True)
        plt.legend()
        plt.xlabel("x")
        plt.ylabel("y")
        plt.title(f"Метод кубической интерполяции. Итерация {iteration}")
        plt.savefig(f"cubic_iter_{iteration}.png", dpi=300, bbox_inches="tight")
        plt.close()

        if abs(derivative_value) < eps:
            return xm, f(xm), np.array(path, dtype=float)

        if derivative_value < 0:
            x0 = xm
        else:
            x1 = xm

        iteration += 1

    return xm, f(xm), np.array(path, dtype=float)


def print_table(path):
    print("Итерация        x0              x1              xm             f'(xm)          f(xm)")
    for row in path:
        print(
            f"{int(row[0]):8d}  "
            f"{row[1]:14.8f}  "
            f"{row[2]:14.8f}  "
            f"{row[3]:14.8f}  "
            f"{row[4]:14.8e}  "
            f"{row[5]:14.8f}"
        )


def main():
    x_min, f_min, path = cubic_interpolation()

    print_table(path)
    print()
    print(f"x* = {x_min:.8f}")
    print(f"f(x*) = {f_min:.8f}")
    print()
    print("Графики сохранены:")
    for i in range(1, len(path) + 1):
        print(f"cubic_iter_{i}.png")


if __name__ == "__main__":
    main()