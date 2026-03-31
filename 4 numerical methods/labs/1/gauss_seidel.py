import numpy as np


def read_from_file(filename):
    with open(filename, 'r') as f:
        first_line = f.readline().split()
        n = int(first_line[0])
        eps = float(first_line[1].replace(',', '.'))
        if len(first_line) >= 3:
            max_iter = int(first_line[2])
        else:
            max_iter = 200
        A = []
        b = []
        for i in range(n):
            row = list(map(float, f.readline().split()))
            A.append(row[:-1])
            b.append(row[-1])
    return np.array(A, dtype=float), np.array(b, dtype=float), eps, max_iter


def input_keyboard():
    n = int(input("Введите количество неизвестных(от 1 до 20): "))
    print("Введите коэффициенты при неизвестных и свободные члены в конце каждой строки "
          "(a_i1 a_i2 ... a_in b_i):")
    A = []
    b = []
    for i in range(n):
        row = list(map(float, input().split()))
        if len(row) != n + 1:
            raise ValueError("Неверное количество элементов в строке")
        A.append(row[:-1])
        b.append(row[-1])
    return np.array(A, dtype=float), np.array(b, dtype=float)


def reorder_rows(A, b):
    n = A.shape[0]
    A = A.copy()
    b = b.copy()
    for i in range(n):
        max_row = i
        max_val = abs(A[i, i])
        for k in range(i + 1, n):
            if abs(A[k, i]) > max_val:
                max_val = abs(A[k, i])
                max_row = k
        if max_row != i:
            A[[i, max_row]] = A[[max_row, i]]
            b[[i, max_row]] = b[[max_row, i]]
    if check_dominance(A):
        return True, A, b
    else:
        return False, A, b


def check_dominance(A):
    n = A.shape[0]
    for i in range(n):
        diag = abs(A[i, i])
        off_diag = sum(abs(A[i, j]) for j in range(n) if j != i)
        if diag < off_diag:
            return False
    return True


def norm_C(A):
    n = A.shape[0]
    norms = []
    for i in range(n):
        s = sum(abs(A[i, j]) for j in range(n) if j != i) / abs(A[i, i])
        norms.append(s)
    return max(norms)


def gauss_seidel(A, b, eps, max_iter):
    n = A.shape[0]
    x = np.zeros(n)
    for i in range(n):
        if A[i, i] == 0:
            raise ValueError("Нулевой диагональный элемент. Метод не применим.")
        x[i] = b[i] / A[i, i]

    errors = []
    for it in range(max_iter):
        x_new = x.copy()
        for i in range(n):
            s1 = np.dot(A[i, :i], x_new[:i])  # j < i
            s2 = np.dot(A[i, i + 1:], x[i + 1:])  # j > i
            x_new[i] = (b[i] - s1 - s2) / A[i, i]

        diff = np.max(np.abs(x_new - x))
        errors.append(diff)
        x = x_new
        if diff < eps:
            return x, it + 1, errors
    return x, max_iter, errors


def main():
    print("Решение СЛАУ методом Гаусса–Зейделя")
    choice = input("Выберите способ ввода (1 - файл, 2 - клавиатура): ")
    if choice == '1':
        filename = input("Имя файла: ")
        A, b, eps, max_iter = read_from_file(filename)
    elif choice == '2':
        A, b = input_keyboard()
        eps = input_float("Введите точность epsilon: ")
        max_iter = int(input("Введите максимальное число итераций: "))
    else:
        print("Неверный выбор")
        return

    n = A.shape[0]
    if n > 20:
        print("Размерность превышает 20.")
        return

    if not check_dominance(A):
        print("Диагональное преобладание отсутствует. Переставим строки")
        success, A_new, b_new = reorder_rows(A, b)
        if success:
            print("После перестановки диагональное преобладание.")
            A, b = A_new, b_new
        else:
            print("Не удалось достичь диагонального преобладания перестановкой строк.")
            print("Метод может расходиться. Продолжить? (y/n): ", end='')
            ans = input()
            if ans.lower() != 'y':
                return
    else:
        print("Диагональное преобладание выполняется.")

    print("\nМатрица после возможных перестановок:")
    print_matrix(A, n)


    norm_c = norm_C(A)
    print(f"Норма матрицы C (по строкам): {norm_c:.6f}")
    if norm_c >= 1:
        print("Так как C >= 1, сходимость не гарантирована.")

    try:
        x, iterations, errors = gauss_seidel(A, b, eps, max_iter)
    except ValueError as e:
        print(e)
        return

    print(f"\nРешение найденое за {iterations} итераций:")
    for i, xi in enumerate(x):
        print(f"x{i + 1} = {xi:.8f}")

    print("\nПогрешности на каждой итерации (max |x^(k) - x^(k-1)|):")
    for k, err in enumerate(errors, 1):
        print(f"итерация {k:3d}: {err:.3e}")


def print_matrix(A, n):
    for i in range(n):
        for j in range(n):
            print(A[i][j], end=' ')
        print()
    print()


def input_float(prompt):
    while True:
        try:
            s = input(prompt).replace(',', '.').strip()
            if not s:
                print("Ошибка: ввод не может быть пустым. Попробуйте снова.")
                continue
            value = float(s)
            return value
        except ValueError:
            print("Ошибка: необходимо ввести число. Попробуйте снова.")


if __name__ == "__main__":
    main()
