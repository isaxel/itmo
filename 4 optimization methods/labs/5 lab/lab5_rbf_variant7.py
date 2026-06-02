import os
import numpy as np
import matplotlib.pyplot as plt
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
PTS = np.column_stack([X, Y])

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rbf_outputs")
os.makedirs(OUT_DIR, exist_ok=True)


def kmeans_init(points, max_iter=100, eps=1e-9):
    centers = np.array([points[0], points[-1]], dtype=float)

    for _ in range(max_iter):
        distances = ((points[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        labels = distances.argmin(axis=1)

        new_centers = centers.copy()
        for j in range(2):
            cluster = points[labels == j]
            if len(cluster) > 0:
                new_centers[j] = cluster.mean(axis=0)

        if np.linalg.norm(new_centers - centers) < eps:
            centers = new_centers
            break
        centers = new_centers

    return centers


def forward(params, points):
    c1 = np.array(params[0:2])
    c2 = np.array(params[2:4])
    sigma = max(params[4], 1e-6)
    w0, w1, w2 = params[5:8]

    r1 = np.sum((points - c1) ** 2, axis=1)
    r2 = np.sum((points - c2) ** 2, axis=1)

    phi1 = np.exp(-r1 / (2 * sigma ** 2))
    phi2 = np.exp(-r2 / (2 * sigma ** 2))

    y_hat = w0 + w1 * phi1 + w2 * phi2
    return y_hat, phi1, phi2, r1, r2


def loss(params, points, target):
    y_hat, _, _, _, _ = forward(params, points)
    return 0.5 * np.mean((y_hat - target) ** 2)


def gradients(params, points, target):
    c1 = np.array(params[0:2])
    c2 = np.array(params[2:4])
    sigma = max(params[4], 1e-6)
    w0, w1, w2 = params[5:8]

    y_hat, phi1, phi2, r1, r2 = forward(params, points)
    e = y_hat - target

    grad_w0 = np.mean(e)
    grad_w1 = np.mean(e * phi1)
    grad_w2 = np.mean(e * phi2)

    grad_c1 = np.mean((e * w1 * phi1)[:, None] * (points - c1) / (sigma ** 2), axis=0)
    grad_c2 = np.mean((e * w2 * phi2)[:, None] * (points - c2) / (sigma ** 2), axis=0)

    grad_sigma = np.mean(e * (w1 * phi1 * r1 + w2 * phi2 * r2) / (sigma ** 3))

    return np.array([
        grad_c1[0], grad_c1[1],
        grad_c2[0], grad_c2[1],
        grad_sigma,
        grad_w0, grad_w1, grad_w2,
    ])


print("=" * 70)
print("ДАТАСЕТ: RBF-АППРОКСИМАЦИЯ")
print("=" * 70)
print("\nТочки (x, y, z):\n")
for i, row in enumerate(DATA):
    print(f"{i}: ({row[0]:.2f}, {row[1]:.2f}) -> z={row[2]:.2f}")
print()

centers = kmeans_init(PTS)
c1_init, c2_init = centers
sigma_init = max(np.linalg.norm(c1_init - c2_init) / 2, 0.5)

params = np.array([
    c1_init[0], c1_init[1],
    c2_init[0], c2_init[1],
    sigma_init,
    0.0, 0.1, -0.1,
], dtype=float)

print("=" * 70)
print("ШАГ 1: ПОИСК ЦЕНТРОВ (K-MEANS)")
print("=" * 70)
print(f"{'Центр':<10}{'cx':<15}{'cy':<15}")
print("-" * 40)
print(f"{'c1':<10}{params[0]:<15.6f}{params[1]:<15.6f}")
print(f"{'c2':<10}{params[2]:<15.6f}{params[3]:<15.6f}")
print()

print("=" * 70)
print("ШАГ 2: НАЧАЛЬНЫЕ ПАРАМЕТРЫ")
print("=" * 70)
print(f"sigma_start = {params[4]:.6f}")
print(f"w0_start    = {params[5]:.6f}")
print(f"w1_start    = {params[6]:.6f}")
print(f"w2_start    = {params[7]:.6f}")
print()

grad0 = gradients(params, PTS, Z)

print("=" * 70)
print("ШАГ 3: ЧАСТНЫЕ ПРОИЗВОДНЫЕ НА ПЕРВОЙ ИТЕРАЦИИ")
print("=" * 70)
print(f"{'Производная':<25}{'Значение':<20}")
print("-" * 45)
print(f"{'dL/dc2_y':<25}{grad0[3]:<20.10f}")
print(f"{'dL/dsigma':<25}{grad0[4]:<20.10f}")
print(f"{'dL/dw0':<25}{grad0[5]:<20.10f}")
print(f"{'dL/dw1':<25}{grad0[6]:<20.10f}")
print()

learning_rate = 0.1
num_iterations = 5000
loss_history = []

print("=" * 70)
print("ШАГ 4: ОБУЧЕНИЕ RBF-СЕТИ")
print("=" * 70)

for iteration in range(num_iterations):
    current_loss = loss(params, PTS, Z)
    loss_history.append(current_loss)

    grad = gradients(params, PTS, Z)
    params = params - learning_rate * grad
    params[4] = max(params[4], 1e-4)

    if iteration % 500 == 0:
        print(f"Итерация {iteration:4d}: loss = {current_loss:.10f}")

final_loss = loss(params, PTS, Z)
y_hat, phi1, phi2, _, _ = forward(params, PTS)
residuals = Z - y_hat

print()
print("=" * 70)
print("ИТОГОВАЯ МОДЕЛЬ RBF")
print("=" * 70)
print("z(x, y) = w0 + w1 * exp(-((x-c1x)^2 + (y-c1y)^2)/(2*sigma^2)) +")
print("          w2 * exp(-((x-c2x)^2 + (y-c2y)^2)/(2*sigma^2))")
print(f"c1 = ({params[0]:.6f}, {params[1]:.6f})")
print(f"c2 = ({params[2]:.6f}, {params[3]:.6f})")
print(f"sigma = {params[4]:.6f}")
print(f"w0 = {params[5]:.6f}")
print(f"w1 = {params[6]:.6f}")
print(f"w2 = {params[7]:.6f}")
print(f"Финальный loss = {final_loss:.12f}")
print()

print("=" * 70)
print("ИТОГОВАЯ ОЦЕНКА")
print("=" * 70)
print(f"{'Объект':<10}{'Факт':<12}{'Прогноз':<14}{'Ошибка':<12}")
print("-" * 48)
for i in range(len(Z)):
    print(f"{i+1:<10}{Z[i]:<12.4f}{y_hat[i]:<14.4f}{abs(residuals[i]):<12.4f}")
print()

plt.figure(figsize=(8, 5))
plt.plot(loss_history)
plt.title("Кривая обучения RBF-сети")
plt.xlabel("Номер итерации")
plt.ylabel("Loss (MSE)")
plt.grid(True)
loss_plot_path = os.path.join(OUT_DIR, "rbf_loss_curve.png")
plt.savefig(loss_plot_path, dpi=300, bbox_inches="tight")
plt.show()


def rbf_surface(x, y, params):
    points = np.column_stack([x.ravel(), y.ravel()])
    z_pred, _, _, _, _ = forward(params, points)
    return z_pred.reshape(x.shape)


x_grid = np.linspace(min(X) - 1, max(X) + 1, 120)
y_grid = np.linspace(min(Y) - 1, max(Y) + 1, 120)
X_grid, Y_grid = np.meshgrid(x_grid, y_grid)
Z_grid = rbf_surface(X_grid, Y_grid, params)

fig = plt.figure(figsize=(14, 6))
ax = fig.add_subplot(121, projection="3d")
ax.plot_surface(X_grid, Y_grid, Z_grid, cmap="viridis", alpha=0.85)
ax.scatter(X, Y, Z, color="red", s=60, label="Точки данных")
ax.set_title("RBF-сеть: модельная поверхность")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")
ax.legend()

ax2 = fig.add_subplot(122)
cont = ax2.contourf(X_grid, Y_grid, Z_grid, levels=25, cmap="viridis")
ax2.scatter(X, Y, c=Z, edgecolors="black", s=70)
ax2.set_title("RBF-сеть: линии уровня")
ax2.set_xlabel("x")
ax2.set_ylabel("y")
fig.colorbar(cont, ax=ax2)

surface_plot_path = os.path.join(OUT_DIR, "rbf_surface_and_contours.png")
plt.savefig(surface_plot_path, dpi=300, bbox_inches="tight")
plt.show()

print("\nФайлы сохранены в папку:")
print(OUT_DIR)
print("- rbf_loss_curve.png")
print("- rbf_surface_and_contours.png")