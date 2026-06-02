import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

DATA = np.array([
    [1.10, 1.10, 0.29],
    [2.01, 1.98, 1.24],
    [3.01, 2.85, 4.94],
    [3.86, 3.99, 4.72],
    [5.10, 4.90, 0.77],
], dtype=float)

X = DATA[:, 0]
Y = DATA[:, 1]
Z = DATA[:, 2]

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gaussian_outputs")
os.makedirs(OUT_DIR, exist_ok=True)

loss_history = []
optimization_log = []

print("=" * 70)
print("ДАТАСЕТ: МОДЕЛИРОВАНИЕ ДВУМЕРНОЙ ГАУССИАНЫ")
print("=" * 70)
print("\nТочки (x, y, z):\n")
for i, row in enumerate(DATA):
    print(f"{i}: ({row[0]:.2f}, {row[1]:.2f}) -> z={row[2]:.2f}")
print()


def gauss_2d(x, y, A, x0, y0, sigma_x, sigma_y, theta=0.0, offset=0.0):
    x_new = (x - x0) * np.cos(theta) + (y - y0) * np.sin(theta)
    y_new = -(x - x0) * np.sin(theta) + (y - y0) * np.cos(theta)
    exponent = -((x_new ** 2) / (2 * sigma_x ** 2) + (y_new ** 2) / (2 * sigma_y ** 2))
    return A * np.exp(exponent) + offset


def loss_function(params):
    A, x0, y0, sigma_x, sigma_y, theta, offset = params
    if A <= 0 or sigma_x <= 0 or sigma_y <= 0:
        return 1e10
    pred = gauss_2d(X, Y, A, x0, y0, sigma_x, sigma_y, theta, offset)
    return 0.5 * np.mean((Z - pred) ** 2)


def callback(params):
    current_loss = loss_function(params)
    loss_history.append(current_loss)

    A, x0, y0, sigma_x, sigma_y, theta, offset = params
    optimization_log.append({
        "iter": len(loss_history) - 1,
        "loss": current_loss,
        "A": A,
        "x0": x0,
        "y0": y0,
        "sigma_x": sigma_x,
        "sigma_y": sigma_y,
        "theta": theta,
        "offset": offset,
    })


max_idx = np.argmax(Z)
params_start = [
    Z[max_idx] + 0.1,
    X[max_idx],
    Y[max_idx],
    np.std(X) * 0.5,
    np.std(Y) * 0.5,
    0.0,
    0.0,
]

print("=" * 70)
print("ШАГ 1: НАЧАЛЬНОЕ ПРИБЛИЖЕНИЕ ПАРАМЕТРОВ")
print("=" * 70)
print(f"A_start       = {params_start[0]:.6f}")
print(f"x0_start      = {params_start[1]:.6f}")
print(f"y0_start      = {params_start[2]:.6f}")
print(f"sigma_x_start = {params_start[3]:.6f}")
print(f"sigma_y_start = {params_start[4]:.6f}")
print(f"theta_start   = {params_start[5]:.6f}")
print(f"offset_start  = {params_start[6]:.6f}")
print()

bounds = [
    (0.1, 10.0),
    (0.0, 6.0),
    (0.0, 6.0),
    (0.1, 5.0),
    (0.1, 5.0),
    (-np.pi / 4, np.pi / 4),
    (-1.0, 1.0),
]

result = minimize(
    loss_function,
    params_start,
    method='L-BFGS-B',
    bounds=bounds,
    callback=callback,
    options={'maxiter': 500}
)

A_opt, x0_opt, y0_opt, sigma_x_opt, sigma_y_opt, theta_opt, offset_opt = result.x
pred = gauss_2d(X, Y, A_opt, x0_opt, y0_opt, sigma_x_opt, sigma_y_opt, theta_opt, offset_opt)
residuals = Z - pred
final_loss = loss_function(result.x)

if not loss_history:
    loss_history = [final_loss]
    optimization_log.append({
        "iter": 0,
        "loss": final_loss,
        "A": A_opt,
        "x0": x0_opt,
        "y0": y0_opt,
        "sigma_x": sigma_x_opt,
        "sigma_y": sigma_y_opt,
        "theta": theta_opt,
        "offset": offset_opt,
    })

print("=" * 95)
print("ШАГ 2: ОПТИМИЗАЦИЯ ПАРАМЕТРОВ (L-BFGS-B)")
print("=" * 95)
print(f"{'Итерация':<10}{'Loss':<15}{'A':<10}{'x0':<10}{'y0':<10}{'sigma_x':<12}{'sigma_y':<12}")
print("-" * 79)

show_count = min(8, len(optimization_log))
if len(optimization_log) <= show_count:
    selected_logs = optimization_log
else:
    idxs = np.linspace(0, len(optimization_log) - 1, show_count, dtype=int)
    selected_logs = [optimization_log[i] for i in idxs]

for row in selected_logs:
    print(
        f"{row['iter']:<10}"
        f"{row['loss']:<15.6f}"
        f"{row['A']:<10.3f}"
        f"{row['x0']:<10.3f}"
        f"{row['y0']:<10.3f}"
        f"{row['sigma_x']:<12.3f}"
        f"{row['sigma_y']:<12.3f}"
    )
print()

print("=" * 95)
print("ИТОГОВАЯ АППРОКСИМИРУЮЩАЯ МОДЕЛЬ")
print("=" * 95)
print("z(x, y) = A * exp(-(x_new^2/(2*sigma_x^2) + y_new^2/(2*sigma_y^2))) + offset")
print(f"A       = {A_opt:.6f}")
print(f"x0      = {x0_opt:.6f}")
print(f"y0      = {y0_opt:.6f}")
print(f"sigma_x = {sigma_x_opt:.6f}")
print(f"sigma_y = {sigma_y_opt:.6f}")
print(f"theta   = {theta_opt:.6f}")
print(f"offset  = {offset_opt:.6f}")
print(f"Финальный loss = {final_loss:.12f}")
print()

print("=" * 70)
print("ИТОГОВАЯ ОЦЕНКА")
print("=" * 70)
print(f"{'Объект':<10}{'Факт':<12}{'Прогноз':<14}{'Ошибка':<12}")
print("-" * 48)
for i in range(len(Z)):
    print(f"{i+1:<10}{Z[i]:<12.4f}{pred[i]:<14.4f}{abs(residuals[i]):<12.4f}")
print()

plt.figure(figsize=(8, 5))
plt.plot(range(1, len(loss_history) + 1), loss_history, marker='o')
plt.title('Кривая сходимости оптимизации')
plt.xlabel('Номер итерации')
plt.ylabel('Loss (0.5 * MSE)')
plt.grid(True)
gauss_loss_path = os.path.join(OUT_DIR, 'gaussian_loss_curve.png')
plt.savefig(gauss_loss_path, dpi=300, bbox_inches='tight')
plt.show()

x_grid = np.linspace(min(X) - 1, max(X) + 1, 120)
y_grid = np.linspace(min(Y) - 1, max(Y) + 1, 120)
X_grid, Y_grid = np.meshgrid(x_grid, y_grid)
Z_grid = gauss_2d(X_grid, Y_grid, A_opt, x0_opt, y0_opt, sigma_x_opt, sigma_y_opt, theta_opt, offset_opt)

fig = plt.figure(figsize=(14, 6))
ax1 = fig.add_subplot(121, projection='3d')
ax1.plot_surface(X_grid, Y_grid, Z_grid, cmap='viridis', alpha=0.85)
ax1.scatter(X, Y, Z, c='red', s=60, label='Точки данных')
ax1.set_title('Двумерная гауссиана: модельная поверхность')
ax1.set_xlabel('x')
ax1.set_ylabel('y')
ax1.set_zlabel('z')
ax1.legend()

ax2 = fig.add_subplot(122)
cont = ax2.contourf(X_grid, Y_grid, Z_grid, levels=25, cmap='viridis')
ax2.scatter(X, Y, c=Z, edgecolors='black', s=70)
ax2.set_title('Двумерная гауссиана: линии уровня')
ax2.set_xlabel('x')
ax2.set_ylabel('y')
fig.colorbar(cont, ax=ax2)

surface_path = os.path.join(OUT_DIR, 'gaussian_surface_and_contours.png')
plt.savefig(surface_path, dpi=300, bbox_inches='tight')
plt.show()

print("\nФайлы сохранены в папку:")
print(OUT_DIR)
print("- gaussian_loss_curve.png")
print("- gaussian_surface_and_contours.png")