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
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "paraboloid_outputs")
os.makedirs(OUT_DIR, exist_ok=True)
loss_history = []


def elliptic_paraboloid(x, y, x0, y0, z0, a, b, theta):
    ct = np.cos(theta)
    st = np.sin(theta)
    u = (x - x0) * ct + (y - y0) * st
    v = -(x - x0) * st + (y - y0) * ct
    return z0 - a * u**2 - b * v**2


def mse_loss(params):
    x0, y0, z0, a, b, theta = params
    if a <= 0 or b <= 0:
        return 1e10
    pred = elliptic_paraboloid(X, Y, x0, y0, z0, a, b, theta)
    return 0.5 * np.mean((Z - pred) ** 2)


def callback(params):
    loss_history.append(mse_loss(params))


initial_params = [X[np.argmax(Z)], Y[np.argmax(Z)], Z.max(), 0.5, 0.5, 0.0]

bounds = [
    (0.0, 6.0),
    (0.0, 6.0),
    (-5.0, 10.0),
    (0.001, 5.0),
    (0.001, 5.0),
    (-np.pi / 2, np.pi / 2),
]

result = minimize(
    mse_loss,
    initial_params,
    method='L-BFGS-B',
    bounds=bounds,
    callback=callback,
    options={'maxiter': 500}
)

x0_opt, y0_opt, z0_opt, a_opt, b_opt, theta_opt = result.x
pred = elliptic_paraboloid(X, Y, x0_opt, y0_opt, z0_opt, a_opt, b_opt, theta_opt)
residuals = Z - pred
final_loss = mse_loss(result.x)

if not loss_history:
    loss_history = [final_loss]

print('=== ЭЛЛИПТИЧЕСКИЙ ПАРАБОЛОИД ===')
print(f'x0 = {x0_opt:.6f}')
print(f'y0 = {y0_opt:.6f}')
print(f'z0 = {z0_opt:.6f}')
print(f'a = {a_opt:.6f}')
print(f'b = {b_opt:.6f}')
print(f'theta = {theta_opt:.6f} рад')
print(f'Финальный loss = {final_loss:.10f}')

print('\nНевязки по объектам:')
for i, (z_true, z_hat, r) in enumerate(zip(Z, pred, residuals), start=1):
    print(f'{i}: z={z_true:.5f}, z_model={z_hat:.5f}, residual={r:.8f}')

print('\nАналитический вид модели:')
print(f'z(x, y) = {z0_opt:.6f} - {a_opt:.6f} * u^2 - {b_opt:.6f} * v^2')
print(f'u = (x - {x0_opt:.6f}) * cos({theta_opt:.6f}) + (y - {y0_opt:.6f}) * sin({theta_opt:.6f})')
print(f'v = -(x - {x0_opt:.6f}) * sin({theta_opt:.6f}) + (y - {y0_opt:.6f}) * cos({theta_opt:.6f})')

plt.figure(figsize=(8, 5))
plt.plot(range(1, len(loss_history) + 1), loss_history, marker='o')
plt.title('Кривая обучения: эллиптический параболоид')
plt.xlabel('Номер итерации')
plt.ylabel('Loss (0.5 * MSE)')
plt.grid(True)
loss_plot_path = os.path.join(OUT_DIR, 'paraboloid_loss_curve.png')
plt.savefig(loss_plot_path, dpi=300, bbox_inches='tight')
plt.show()

x_grid = np.linspace(min(X) - 1, max(X) + 1, 140)
y_grid = np.linspace(min(Y) - 1, max(Y) + 1, 140)
Xg, Yg = np.meshgrid(x_grid, y_grid)
Zg = elliptic_paraboloid(Xg, Yg, x0_opt, y0_opt, z0_opt, a_opt, b_opt, theta_opt)

fig = plt.figure(figsize=(14, 6))
ax1 = fig.add_subplot(121, projection='3d')
ax1.plot_surface(Xg, Yg, Zg, cmap='viridis', alpha=0.82)
ax1.scatter(X, Y, Z, c='red', s=60, label='Данные')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')
ax1.set_title('Эллиптический параболоид: 3D')
ax1.legend()

ax2 = fig.add_subplot(122)
contour = ax2.contourf(Xg, Yg, Zg, levels=25, cmap='viridis', alpha=0.9)
ax2.scatter(X, Y, c=Z, s=120, edgecolors='black', cmap='viridis', label='Точки данных')
ax2.contour(Xg, Yg, Zg, levels=12, colors='white', linewidths=0.5, alpha=0.35)
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.set_title('Линии уровня и точки данных')
ax2.grid(True, alpha=0.3)
ax2.legend()
plt.colorbar(contour, ax=ax2, label='Z')
plt.tight_layout()
surface_plot_path = os.path.join(OUT_DIR, 'paraboloid_surface_and_contours.png')
plt.savefig(surface_plot_path, dpi=300, bbox_inches='tight')
plt.show()

print('\nФайлы сохранены в папку:')
print(OUT_DIR)
print('- paraboloid_loss_curve.png')
print('- paraboloid_surface_and_contours.png')
