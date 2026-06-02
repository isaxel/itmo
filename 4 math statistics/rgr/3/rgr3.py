import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy.stats import t


df = pd.read_csv('RGR3_A_5.csv')
x = df['x'].values
y = df['y'].values
n = len(df)

#Диаграмма рассеяния ---
plt.figure(figsize=(10, 6))
plt.scatter(x, y, color='dodgerblue', alpha=0.7, edgecolors='k', label='Фактические данные')
plt.title('Диаграмма рассеяния: Скорость записи от скорости чтения')
plt.xlabel('Скорость чтения (x), МБ/с')
plt.ylabel('Скорость записи (y), МБ/с')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.show()

#Построение моделей
# Линейная
X_lin = sm.add_constant(x) # Добавляем константу (свободный член 'a')
model_lin = sm.OLS(y, X_lin).fit()
y_pred_lin = model_lin.predict(X_lin)

# Квадратичная
X_quad = np.column_stack((x, x**2))
X_quad = sm.add_constant(X_quad)
model_quad = sm.OLS(y, X_quad).fit()
y_pred_quad = model_quad.predict(X_quad)

# Степенная
ln_x = np.log(x)
ln_y = np.log(y)
X_pow = sm.add_constant(ln_x)
model_pow_log = sm.OLS(ln_y, X_pow).fit()

#Возвращаемся от логарифмов к исходным переменным
a_pow = np.exp(model_pow_log.params[0])
b_pow = model_pow_log.params[1]
y_pred_pow = a_pow * (x ** b_pow)

#Сравнение моделей
def calc_metrics(y_true, y_pred):
    # Коэффициент детерминации R^2
    r2 = 1 - np.sum((y_true - y_pred)**2) / np.sum((y_true - np.mean(y_true))**2)
    # RMSE
    rmse = np.sqrt(np.mean((y_true - y_pred)**2))
    # Средняя ошибка аппроксимации A (%)
    A = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    return r2, rmse, A

r2_lin, rmse_lin, A_lin = calc_metrics(y, y_pred_lin)
r2_quad, rmse_quad, A_quad = calc_metrics(y, y_pred_quad)
r2_pow, rmse_pow, A_pow = calc_metrics(y, y_pred_pow)

print("--- СРАВНЕНИЕ МОДЕЛЕЙ ---")
print(f"Линейная:     R^2 = {r2_lin:.4f}, RMSE = {rmse_lin:.4f}, A = {A_lin:.2f}%")
print(f"Квадратичная: R^2 = {r2_quad:.4f}, RMSE = {rmse_quad:.4f}, A = {A_quad:.2f}%")
print(f"Степенная:    R^2 = {r2_pow:.4f}, RMSE = {rmse_pow:.4f}, A = {A_pow:.2f}%")

# Графики сравнения моделей
x_plot = np.linspace(min(x), max(x), 200)
y_plot_lin = model_lin.params[0] + model_lin.params[1] * x_plot
y_plot_quad = model_quad.params[0] + model_quad.params[1] * x_plot + model_quad.params[2] * (x_plot**2)
y_plot_pow = a_pow * (x_plot ** b_pow)

plt.figure(figsize=(10, 6))
plt.scatter(x, y, color='lightgray', edgecolors='k', alpha=0.6, label='Данные')
plt.plot(x_plot, y_plot_lin, color='red', linewidth=2, label='Линейная')
plt.plot(x_plot, y_plot_quad, color='green', linewidth=2, label='Квадратичная')
plt.plot(x_plot, y_plot_pow, color='blue', linewidth=2, label='Степенная')
plt.title('Линии регрессии для разных моделей')
plt.xlabel('Скорость чтения (x)')
plt.ylabel('Скорость записи (y)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.6)
plt.show()

#Анализ линейной модели
residuals = y - y_pred_lin
RSS = np.sum(residuals**2)
s2 = RSS / (n - 2) # Оценка дисперсии ошибки

print("\n--- ДЕТАЛЬНЫЙ АНАЛИЗ ЛИНЕЙНОЙ МОДЕЛИ ---")
print(f"Уравнение линейной регрессии: y = {model_lin.params[0]:.4f} + {model_lin.params[1]:.4f} * x")
print(f"Остаточная сумма квадратов (RSS): {RSS:.4f}")
print(f"Оценка дисперсии ошибки (s^2): {s2:.4f}")

# Расчет доверительных интервалов
alpha = 0.05
t_crit = t.ppf(1 - alpha/2, df=n-2) # t-критическое
std_err = model_lin.bse # Стандартные ошибки коэффициентов

ci_lower = model_lin.params - t_crit * std_err
ci_upper = model_lin.params + t_crit * std_err

print(f"\nДоверительные интервалы (уровень надежности 95%):")
print(f"Для параметра 'a' (свободный член): [{ci_lower[0]:.4f}; {ci_upper[0]:.4f}]")
print(f"Для параметра 'b' (коэффициент при x): [{ci_lower[1]:.4f}; {ci_upper[1]:.4f}]")

# === ПРОГНОЗ ПО ТРЁМ МОДЕЛЯМ ===
x_star = 1207.9904

# 1) Линейная модель: y = a + b*x
y_star_lin = model_lin.params[0] + model_lin.params[1] * x_star

# 2) Квадратичная модель: y = a + b*x + c*x^2
y_star_quad = (model_quad.params[0] + 
               model_quad.params[1] * x_star + 
               model_quad.params[2] * (x_star**2))


# 3) Степенная модель: y = a * x^b
#    (a_pow и b_pow уже получены при линеаризации)
y_star_pow = a_pow * (x_star ** b_pow)

print("\n--- ПРОГНОЗЫ ПО ТРЁМ МОДЕЛЯМ ---")
print(f"Уравнение линейной регрессии: y = {model_lin.params[0]:.4f} + {model_lin.params[1]:.4f} * x")
print(f"Линейная модель:     y* = {y_star_lin:.4f} МБ/с")

print(f"Уравнение квадратичной регрессии: y = {model_quad.params[0]:.4f} + {model_quad.params[1]:.4f} * x + {model_quad.params[2]:.4f} * x**2" )
print(f"Квадратичная модель: y* = {y_star_quad:.4f} МБ/с")

print(f"Уравнение степенной регрессии: y = {a_pow} * x ^ {b_pow}")
print(f"Степенная модель:    y* = {y_star_pow:.4f} МБ/с")
