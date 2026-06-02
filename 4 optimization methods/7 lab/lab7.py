import numpy as np
import matplotlib.pyplot as plt
import torch

def f(x, y):
    return 10**(-2) * (8*x**2 + 2*x*y + 35*x + 8*y + 12)


def grad(x, y):
    fx = 10**(-2) * (16*x + 2*y + 35)
    fy = 10**(-2) * (2*x + 8)
    return np.array([fx, fy])

saddle = np.array([-4.0, 14.5])
global_min = np.array([4.0625, -50.0])

x0 = np.array([-13.912, 13.179])
n_iter = 100

def plot_path(history, bounds, title, filename, show_global_min=True):
    x_min, x_max, y_min, y_max = bounds

    x = np.linspace(x_min, x_max, 500)
    y = np.linspace(y_min, y_max, 500)

    X, Y = np.meshgrid(x, y)
    Z = f(X, Y)

    plt.figure(figsize=(9, 6))
    plt.contour(X, Y, Z, levels=40)

    plt.plot(
        history[:, 0],
        history[:, 1],
        marker='.',
        markersize=4,
        linewidth=1.5,
        label='Последовательные приближения'
    )

    plt.scatter(
        history[0, 0],
        history[0, 1],
        marker='o',
        s=90,
        label='Начало'
    )

    plt.scatter(
        saddle[0],
        saddle[1],
        marker='x',
        s=120,
        label='Седловая точка'
    )

    if show_global_min:
        plt.scatter(
            global_min[0],
            global_min[1],
            marker='s',
            s=90,
            label='Глобальный минимум'
        )

    plt.xlabel('x')
    plt.ylabel('y')
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()

def gradient_descent(x0, alpha, n_iter):
    x = x0.copy()
    history = [x.copy()]

    for i in range(n_iter):
        g = grad(x[0], x[1])
        x = x - alpha * g
        history.append(x.copy())

    return np.array(history)


alpha_gd = 0.5
gd_history = gradient_descent(x0, alpha_gd, n_iter)

print("2.1 Обычный градиентный спуск")
print("x0 =", x0)
print("alpha =", alpha_gd)
print("количество итераций =", n_iter)
print("последняя точка =", gd_history[-1])
print("седловая точка =", saddle)
print("расстояние до седловой точки =", np.linalg.norm(gd_history[-1] - saddle))
print("норма градиента =", np.linalg.norm(grad(gd_history[-1, 0], gd_history[-1, 1])))
print("f =", f(gd_history[-1, 0], gd_history[-1, 1]))


plot_path(
    gd_history,
    bounds=(-16, 2, 10, 16),
    title="Обычный градиентный спуск",
    filename="task2_1_gradient_descent.png",
    show_global_min=False
)

def polyak_method(x0, alpha, beta, n_iter):
    x_prev = x0.copy()
    x = x0.copy()
    history = [x.copy()]

    for i in range(n_iter):
        g = grad(x[0], x[1])
        x_next = x - alpha * g + beta * (x - x_prev)

        x_prev = x.copy()
        x = x_next.copy()

        history.append(x.copy())

    return np.array(history)


alpha_polyak = 2.5
beta_polyak = 0.95

polyak_history = polyak_method(x0, alpha_polyak, beta_polyak, n_iter)

print("\n2.2 Метод Поляка")
print("alpha =", alpha_polyak)
print("beta =", beta_polyak)
print("последняя точка =", polyak_history[-1])
print("расстояние до седловой точки =", np.linalg.norm(polyak_history[-1] - saddle))
print("f =", f(polyak_history[-1, 0], polyak_history[-1, 1]))


plot_path(
    polyak_history,
    bounds=(-16, 8, -50, 18),
    title="Метод Поляка",
    filename="task2_2_polyak.png",
    show_global_min=True
)

alpha_zigzag = 3.0
beta_zigzag = 0.95

zigzag_history = polyak_method(x0, alpha_zigzag, beta_zigzag, n_iter)

print("\n2.3 Пилообразная траектория")
print("alpha =", alpha_zigzag)
print("beta =", beta_zigzag)
print("последняя точка =", zigzag_history[-1])
print("f =", f(zigzag_history[-1, 0], zigzag_history[-1, 1]))


plot_path(
    zigzag_history,
    bounds=(-16, 8, -50, 18),
    title="Метод Поляка: пилообразная траектория",
    filename="task2_3_zigzag.png",
    show_global_min=True
)

alpha_smooth = 2.0
beta_smooth = 0.98

smooth_history = polyak_method(x0, alpha_smooth, beta_smooth, n_iter)

print("\n2.3 Более ровная траектория")
print("alpha =", alpha_smooth)
print("beta =", beta_smooth)
print("последняя точка =", smooth_history[-1])
print("f =", f(smooth_history[-1, 0], smooth_history[-1, 1]))


plot_path(
    smooth_history,
    bounds=(-16, 8, -50, 18),
    title="Метод Поляка: более ровная траектория",
    filename="task2_3_smooth.png",
    show_global_min=True
)

def torch_f(z):
    x = z[0]
    y = z[1]
    return 10**(-2) * (8*x**2 + 2*x*y + 35*x + 8*y + 12)


def torch_sgd_momentum(x0, alpha, beta, n_iter):
    z = torch.tensor(x0, dtype=torch.float32, requires_grad=True)

    optimizer = torch.optim.SGD(
        [z],
        lr=alpha,
        momentum=beta
    )

    history = []

    for i in range(n_iter + 1):
        history.append(z.detach().numpy().copy())

        optimizer.zero_grad()
        loss = torch_f(z)
        loss.backward()
        optimizer.step()

    return np.array(history)


alpha_torch = 2.0
beta_torch = 0.98

torch_history = torch_sgd_momentum(x0, alpha_torch, beta_torch, n_iter)

print("\n2.4 PyTorch SGD с momentum")
print("alpha =", alpha_torch)
print("beta =", beta_torch)
print("последняя точка =", torch_history[-1])
print("f =", f(torch_history[-1, 0], torch_history[-1, 1]))


plot_path(
    torch_history,
    bounds=(-16, 8, -50, 18),
    title="PyTorch SGD с momentum",
    filename="task2_4_pytorch.png",
    show_global_min=True
)
