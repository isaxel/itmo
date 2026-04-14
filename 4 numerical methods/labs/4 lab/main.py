import numpy as np
import matplotlib.pyplot as plt
import os
import warnings

warnings.filterwarnings('ignore', category=RuntimeWarning)


def safe_float_convert(val_str):
    val_str = val_str.replace(',', '.')
    if val_str.count('.') > 1:
        raise ValueError
    return float(val_str)


def get_array_from_input(prompt):
    while True:
        try:
            raw_input = input(prompt).strip()
            if not raw_input: continue
            arr = [safe_float_convert(x) for x in raw_input.split()]
            return np.array(arr)
        except ValueError:
            print("Ошибка: Неверный формат чисел.")


def calculate_and_process(x_data, y_data):
    n = len(x_data)

    sum_y = np.sum(y_data)
    sum_y_sq = np.sum(y_data ** 2)
    s_total = sum_y_sq - (sum_y ** 2) / n

    models_data = {}
    skipped_models = []

    for degree, name in zip([1, 2, 3], ["Линейная", "Квадратичная", "Кубическая"]):
        coeffs = np.polyfit(x_data, y_data, degree)
        p = np.poly1d(coeffs)
        s_res = np.sum((p(x_data) - y_data) ** 2)

        r2 = 1 - (s_res / s_total) if s_total != 0 else 0

        if degree == 1:
            formula = f"y = {coeffs[0]:.2f}x + {coeffs[1]:.2f}"
        elif degree == 2:
            formula = f"y = {coeffs[0]:.2f}x² + {coeffs[1]:.2f}x + {coeffs[2]:.2f}"
        else:
            formula = f"y = {coeffs[0]:.3f}x³ + {coeffs[1]:.2f}x² + ..."

        models_data[name] = {"func": p, "delta": np.sqrt(s_res / n), "r2": r2, "formula": formula}

    if np.all(y_data > 0):
        c = np.polyfit(x_data, np.log(y_data), 1)
        a, b = np.exp(c[1]), c[0]
        f_exp = lambda x, a=a, b=b: a * np.exp(b * x)
        s_res = np.sum((f_exp(x_data) - y_data) ** 2)
        r2 = 1 - (s_res / s_total) if s_total != 0 else 0
        models_data["Экспоненциальная"] = {
            "func": f_exp, "delta": np.sqrt(s_res / n), "r2": r2,
            "formula": f"y = {a:.2f} * exp({b:.2f}x)"
        }
    else:
        skipped_models.append("Экспоненциальная")

    if np.all(x_data > 0):
        c = np.polyfit(np.log(x_data), y_data, 1)
        a, b = c[0], c[1]
        f_log = lambda x, a=a, b=b: a * np.log(x) + b
        s_res = np.sum((f_log(x_data) - y_data) ** 2)
        r2 = 1 - (s_res / s_total) if s_total != 0 else 0
        models_data["Логарифмическая"] = {
            "func": f_log, "delta": np.sqrt(s_res / n), "r2": r2,
            "formula": f"y = {a:.2f}ln(x) + {b:.2f}"
        }
    else:
        skipped_models.append("Логарифмическая")

    if np.all(x_data > 0) and np.all(y_data > 0):
        c = np.polyfit(np.log(x_data), np.log(y_data), 1)
        a, b = np.exp(c[1]), c[0]
        f_pow = lambda x, a=a, b=b: a * (x ** b)
        s_res = np.sum((f_pow(x_data) - y_data) ** 2)
        r2 = 1 - (s_res / s_total) if s_total != 0 else 0
        models_data["Степенная"] = {
            "func": f_pow, "delta": np.sqrt(s_res / n), "r2": r2,
            "formula": f"y = {a:.2f} * x^{b:.2f}"
        }
    else:
        skipped_models.append("Степенная")

    print("\nРезультаты аппроксимации")
    for name, data in models_data.items():
        print(f"{name}: СКО={data['delta']:.4f}, R²={data['r2']:.4f}")

    best_name = min(models_data, key=lambda k: models_data[k]["delta"])
    print(f"\nНаилучшая модель: {best_name}")

    x_plot = np.linspace(min(x_data) - 0.5, max(x_data) + 0.5, 500)
    plt.figure(figsize=(14, 8))
    plt.scatter(x_data, y_data, color='black', label='Исходные данные', zorder=10, s=60)

    colors = {
        "Линейная": "blue", "Квадратичная": "green", "Кубическая": "red",
        "Экспоненциальная": "orange", "Логарифмическая": "purple", "Степенная": "brown"
    }

    for name, data in models_data.items():
        y_val = data["func"](x_plot)
        y_val = np.where((y_val < 1e6) & (y_val > -1e6), y_val, np.nan)

        legend_label = f"{name}\n{data['formula']}\n$R^2$ = {data['r2']:.3f}"
        plt.plot(x_plot, y_val, label=legend_label, color=colors[name], linewidth=2)

    plt.title('Сравнение моделей аппроксимации', fontsize=14)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=9)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.ylim(min(y_data) - 5, max(y_data) + 5)
    plt.show()


def main():
    while True:
        print("\n1. Ввод вручную\n2. Из файла\n0. Выход")
        choice = input("Ваш выбор: ").strip()
        if choice == '1':
            x = get_array_from_input("X: ")
            y = get_array_from_input("Y: ")
            if len(x) == len(y) and len(np.unique(x)) >= 4:
                calculate_and_process(x, y)
            else:
                print("Ошибка: недостаточно точек или разная длина.")
        elif choice == '2':
            fname = input("Имя файла: ").strip()
            if os.path.exists(fname):
                with open(fname, 'r') as f:
                    lines = [l.strip() for l in f if l.strip()]
                x = np.array([safe_float_convert(i) for i in lines[0].split()])
                y = np.array([safe_float_convert(i) for i in lines[1].split()])
                calculate_and_process(x, y)
        elif choice == '0':
            break
        else:
            print("Введите 0, 1 или 2.")


if __name__ == "__main__":
    main()