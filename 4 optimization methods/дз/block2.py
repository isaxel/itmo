# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
import numpy as np
import matplotlib.pyplot as plt


EPS = 1e-4


class ObjectiveFunction:
    def __init__(self, func, grad, hess=None):
        self.func = func
        self.grad = grad
        self.hess = hess

    def value(self, x):
        return self.func(x)

    def gradient(self, x):
        return self.grad(x)

    def hessian(self, x):
        if self.hess is None:
            raise ValueError("Матрица Гессе не задана")
        return self.hess(x)


class Optimizer(ABC):
    def __init__(self, objective, start, eps=EPS, max_iter=1000):
        self.objective = objective
        self.start = np.array(start, dtype=float)
        self.eps = eps
        self.max_iter = max_iter
        self.path = []

    @abstractmethod
    def step(self, x):
        pass

    def optimize(self):
        x = self.start.copy()
        self.path = [x.copy()]

        for _ in range(self.max_iter):
            g = self.objective.gradient(x)

            if np.linalg.norm(g) < self.eps:
                break

            x_new = self.step(x)
            self.path.append(x_new.copy())

            if np.linalg.norm(x_new - x) < 1e-12:
                x = x_new
                break

            x = x_new

        return x, self.objective.value(x), np.array(self.path)


class CoordinateDescent(Optimizer):
    def step(self, x):
        x = x.copy()

        x[0] = -(2*x[1] + 10) / 4
        self.path.append(x.copy())

        x[1] = (10 - 2*x[0]) / 6

        return x


class GradientDescent(Optimizer):
    def __init__(self, objective, start, alpha=0.12, **kwargs):
        super().__init__(objective, start, **kwargs)
        self.alpha = alpha

    def step(self, x):
        g = self.objective.gradient(x)
        return x - self.alpha * g


class SteepestDescent(Optimizer):
    def step(self, x):
        g = self.objective.gradient(x)
        H = self.objective.hessian(x)

        alpha = (g @ g) / (g @ H @ g)

        return x - alpha * g


class NewtonMethod(Optimizer):
    def step(self, x):
        g = self.objective.gradient(x)
        H = self.objective.hessian(x)

        delta = np.linalg.solve(H, -g)

        return x + delta


def f_lr4(x):
    x1, x2 = x[0], x[1]
    return 2*x1**2 + 2*x1*x2 + 3*x2**2 + 10*x1 - 10*x2 + 35


def grad_lr4(x):
    x1, x2 = x[0], x[1]
    return np.array([
        4*x1 + 2*x2 + 10,
        2*x1 + 6*x2 - 10
    ], dtype=float)


def hess_lr4(x):
    return np.array([
        [4.0, 2.0],
        [2.0, 6.0]
    ])


def z_newton(x):
    x1, x2 = x[0], x[1]
    return x1**3 - 3*x1 + x2**3 + x2**2 - x2 - 3


def grad_newton(x):
    x1, x2 = x[0], x[1]
    return np.array([
        3*x1**2 - 3,
        3*x2**2 + 2*x2 - 1
    ], dtype=float)


def hess_newton(x):
    x1, x2 = x[0], x[1]
    return np.array([
        [6*x1, 0.0],
        [0.0, 6*x2 + 2]
    ], dtype=float)


def analytical_minimum_lr4():
    H = np.array([
        [4.0, 2.0],
        [2.0, 6.0]
    ])
    b = np.array([10.0, -10.0])
    x_star = -np.linalg.solve(H, b)

    return x_star, f_lr4(x_star)


def make_levels_from_path(func, path):
    raw_levels = np.array([func(p) for p in path], dtype=float)
    raw_levels = np.sort(raw_levels)

    levels = []

    for value in raw_levels:
        if not levels or abs(value - levels[-1]) > 1e-7:
            levels.append(value)

    return np.array(levels)


def plot_path(func, path, title, filename, true_minimum=None):
    path = np.array(path)

    if true_minimum is not None:
        all_points = np.vstack([path, true_minimum])
    else:
        all_points = path

    margin = 1.0

    x_min = all_points[:, 0].min() - margin
    x_max = all_points[:, 0].max() + margin
    y_min = all_points[:, 1].min() - margin
    y_max = all_points[:, 1].max() + margin

    X, Y = np.meshgrid(
        np.linspace(x_min, x_max, 500),
        np.linspace(y_min, y_max, 500)
    )

    Z = func([X, Y])
    levels = make_levels_from_path(func, path)

    plt.figure(figsize=(10, 7))

    if len(levels) > 1:
        main_contours = plt.contour(
            X, Y, Z,
            levels=levels,
            linewidths=1.4
        )
        plt.clabel(main_contours, inline=True, fontsize=8)

    plt.plot(
        path[:, 0],
        path[:, 1],
        "o-",
        linewidth=2.3,
        markersize=5,
        label="Ломаная приближений"
    )

    plt.scatter(
        path[0, 0],
        path[0, 1],
        s=100,
        marker="o",
        label="Начальная точка"
    )

    plt.scatter(
        path[-1, 0],
        path[-1, 1],
        s=160,
        marker="*",
        label="Последнее приближение"
    )

    if true_minimum is not None:
        plt.scatter(
            true_minimum[0],
            true_minimum[1],
            s=130,
            marker="x",
            label="Аналитический минимум"
        )

    indices = list(range(min(8, len(path))))

    if len(path) - 1 not in indices:
        indices.append(len(path) - 1)

    for k in indices:
        p = path[k]
        plt.annotate(
            str(k),
            (p[0], p[1]),
            textcoords="offset points",
            xytext=(6, 6),
            fontsize=9
        )

    plt.title(title)
    plt.xlabel("x1")
    plt.ylabel("x2")
    plt.grid(True, linestyle="--", alpha=0.45)
    plt.legend(loc="best")
    plt.gca().set_aspect("equal", adjustable="box")
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()


def print_iterations(name, objective, path):
    print("\n" + name)
    print("-" * len(name))
    print(" k        x1              x2              f(x)            ||grad||")

    for k, x in enumerate(path):
        print(
            f"{k:2d}  "
            f"{x[0]:14.8f}  "
            f"{x[1]:14.8f}  "
            f"{objective.value(x):14.8f}  "
            f"{np.linalg.norm(objective.gradient(x)):14.8e}"
        )


def main():
    print("=" * 80)
    print("Блок 2. Вариант 7. Объектная модель")
    print("=" * 80)

    x_star_lr4, f_star_lr4 = analytical_minimum_lr4()

    objective_lr4 = ObjectiveFunction(
        func=f_lr4,
        grad=grad_lr4,
        hess=hess_lr4
    )

    start_lr4 = np.array([2.0, -3.0])

    optimizers = [
        (
            "Покоординатный спуск",
            CoordinateDescent(objective_lr4, start_lr4),
            "block2_coordinate_descent.png"
        ),
        (
            "Градиентный спуск",
            GradientDescent(objective_lr4, start_lr4, alpha=0.12),
            "block2_gradient_descent.png"
        ),
        (
            "Наискорейший спуск",
            SteepestDescent(objective_lr4, start_lr4),
            "block2_steepest_descent.png"
        )
    ]

    print("\nФункция из ЛР4:")
    print("f(x1,x2) = 2*x1^2 + 2*x1*x2 + 3*x2^2 + 10*x1 - 10*x2 + 35")
    print(f"Аналитический минимум: x* = ({x_star_lr4[0]:.8f}, {x_star_lr4[1]:.8f})")
    print(f"f(x*) = {f_star_lr4:.8f}")

    for name, optimizer, filename in optimizers:
        x_min, f_min, path = optimizer.optimize()

        print_iterations(name, objective_lr4, path)

        plot_path(
            f_lr4,
            path,
            name + ": линии уровня и ломаная приближений",
            filename,
            true_minimum=x_star_lr4
        )

    objective_newton = ObjectiveFunction(
        func=z_newton,
        grad=grad_newton,
        hess=hess_newton
    )

    start_newton = np.array([0.5, 0.5])
    newton = NewtonMethod(objective_newton, start_newton)

    x_min_newton, f_min_newton, path_newton = newton.optimize()

    print_iterations("Метод Ньютона", objective_newton, path_newton)

    true_min_newton = np.array([1.0, 1.0/3.0])

    plot_path(
        z_newton,
        path_newton,
        "Метод Ньютона: линии уровня и траектория приближений",
        "block2_newton_method.png",
        true_minimum=true_min_newton
    )

if __name__ == "__main__":
    main()