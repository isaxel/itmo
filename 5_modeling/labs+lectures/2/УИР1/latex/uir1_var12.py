import sys, numpy as np, openpyxl
from scipy import stats
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

XLSX = sys.argv[1] if len(sys.argv) > 1 else "!_УИР1_Варианты_с.xlsx"
OUT = sys.argv[2] if len(sys.argv) > 2 else "."
VAR = 12
NS = (10, 20, 50, 100, 200, 300)
PS = (0.90, 0.95, 0.99)

ws = openpyxl.load_workbook(XLSX, data_only=True)["1-50"]
assert ws.cell(1, VAR + 1).value == VAR
x = np.array([ws.cell(r, VAR + 1).value for r in range(2, 302)], float)


def chars(a):
    n = len(a)
    m = a.mean()
    D = a.var(ddof=1)
    s = np.sqrt(D)
    r = {"m": m, "D": D, "s": s, "cv": s / m}
    for p in PS:
        r[p] = stats.norm.ppf((1 + p) / 2) * s / np.sqrt(n)
    return r


def acf(a, K=10):
    return np.array([np.corrcoef(a[:-k], a[k:])[0, 1] for k in range(1, K + 1)])


def table(R, ref, title):
    rows = [
        ("Мат.ож.", "m"),
        ("Дов.инт.(0,9)", 0.90),
        ("Дов.инт.(0,95)", 0.95),
        ("Дов.инт.(0,99)", 0.99),
        ("Дисперсия", "D"),
        ("С.к.о.", "s"),
        ("К-т вариации", "cv"),
    ]
    print(f"\n{title}\n{'':22}" + "".join(f"{n:>11}" for n in NS))
    for name, k in rows:
        pre = "+-" if isinstance(k, float) else ""
        print(f"{name:16}знач. " + "".join(f"{pre+format(R[n][k], '.3f'):>11}" for n in NS))
        print(
            f"{'':16}%     "
            + "".join(f"{(R[n][k]-ref[n][k])/ref[n][k]*100:>11.1f}" for n in NS)
        )


R = {n: chars(x[:n]) for n in NS}
ref300 = {n: R[300] for n in NS}
table(R, ref300, f"ФОРМА 1. Характеристики заданной ЧП; % - от n=300")

m, cv = R[300]["m"], R[300]["cv"]
ac_x = acf(x)
lr = stats.linregress(np.arange(1, 301), x)
print(f"\nТренд: y = {lr.intercept:.2f} + {lr.slope:.4f}*i, p-value = {lr.pvalue:.3f}")
print(
    "АК заданной ЧП:",
    np.round(ac_x, 3),
    " граница значимости +-",
    round(1.96 / np.sqrt(300), 3),
)

t2 = m * (2 - np.sqrt(6 * cv**2 - 2)) / 6
t1 = m - 2 * t2
phases = np.array([t1, t2, t2])
print(f"\nnu = {cv:.4f}, 1/nu^2 = {1/cv**2:.3f}")
print(
    f"Гипоэкспоненциальное: t1 = {t1:.3f}, t2 = t3 = {t2:.3f}; lambda1 = {1/t1:.5f}, lambda2 = lambda3 = {1/t2:.5f}"
)
print(
    f"  проверка: M = {phases.sum():.3f}, nu = {np.sqrt((phases**2).sum())/phases.sum():.4f}"
)
print(
    f"Для сравнения Эрланг 3-го порядка: lambda = k/m = {3/m:.5f}, nu = {1/np.sqrt(3):.4f}"
)

rng = np.random.default_rng(12)


def gen_hypo(n):
    r = rng.random((n, 3))
    return -(np.log(r) * phases).sum(axis=1)


y = gen_hypo(300)


def hypo_pdf(t):
    a, b = 1 / t1, 1 / t2
    c = b - a
    return a * b**2 * (np.exp(-a * t) - np.exp(-b * t) * (1 + c * t)) / c**2


G = {n: chars(y[:n]) for n in NS}
table(
    G,
    R,
    "ФОРМА 2. Характеристики сгенерированной ЧП (гипоэкспоненциальный закон); % - от заданной ЧП",
)
ac_y = acf(y)
print("\nФОРМА 3. Сдвиг:      " + "".join(f"{k:>8}" for k in range(1, 11)))
print("АК заданной ЧП      " + "".join(f"{v:>8.3f}" for v in ac_x))
print("АК сгенерир. ЧП     " + "".join(f"{v:>8.3f}" for v in ac_y))
print("|разность|          " + "".join(f"{abs(a-b):>8.3f}" for a, b in zip(ac_x, ac_y)))
r_xy = np.corrcoef(x, y)[0, 1]
print(f"\nКоэффициент корреляции заданной и сгенерированной ЧП: {r_xy:.4f}")

grid = np.linspace(0, 5000, 200001)
from scipy.integrate import cumulative_trapezoid

cdf_grid = cumulative_trapezoid(
    np.nan_to_num(hypo_pdf(np.maximum(grid, 1e-9))), grid, initial=0
)
ks_h = stats.kstest(x, lambda t: np.interp(t, grid, cdf_grid))
ks_e = stats.kstest(x, stats.gamma(a=3, scale=m / 3).cdf)
ks_x = stats.kstest(x, stats.expon(scale=m).cdf)
ks_g = stats.ks_2samp(x, y)
print(
    f"KS: гипоэксп. D={ks_h.statistic:.4f} p={ks_h.pvalue:.3f}; Эрланг-3 D={ks_e.statistic:.4f} p={ks_e.pvalue:.3f}; "
    f"экспон. D={ks_x.statistic:.4f} p={ks_x.pvalue:.4f}; две выборки D={ks_g.statistic:.4f} p={ks_g.pvalue:.3f}"
)
mean_h = cumulative_trapezoid(grid * hypo_pdf(np.maximum(grid, 1e-9)), grid)[-1]
print(f"  контроль плотности: intf = {cdf_grid[-1]:.4f}, intt*f = {mean_h:.3f}")

plt.rcParams.update({"font.size": 10, "figure.dpi": 130})
i = np.arange(1, 301)
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(i, x, lw=0.9, color="#2f6db5", label="Заданная ЧП")
ax.plot(
    i,
    lr.intercept + lr.slope * i,
    "--",
    color="#c0392b",
    label=f"Линейный тренд, наклон {lr.slope:.3f}",
)
ax.axhline(m, color="gray", lw=0.8, ls=":", label=f"Среднее {m:.1f}")
ax.set(
    xlabel="Номер значения i",
    ylabel="x_i",
    title="График 1. Значения заданной числовой последовательности",
)
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(f"{OUT}/График1_ЧП.png")

fig, ax = plt.subplots(figsize=(8, 4))
k = np.arange(1, 11)
ax.bar(k - 0.2, ac_x, 0.4, label="Заданная ЧП", color="#2f6db5")
ax.bar(k + 0.2, ac_y, 0.4, label="Сгенерированная ЧП", color="#e67e22")
for s in (1, -1):
    ax.axhline(s * 1.96 / np.sqrt(300), color="#c0392b", ls="--", lw=0.8)
ax.axhline(0, color="black", lw=0.6)
ax.set(
    xlabel="Сдвиг k",
    ylabel="r(k)",
    title="Коэффициенты автокорреляции (пунктир - +-1,96/sqrtn)",
    xticks=k,
)
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(f"{OUT}/Автокорреляция.png")

bins = np.arange(0, 1250, 50)
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.hist(x, bins=bins, color="#2f6db5", edgecolor="white")
ax.set(
    xlabel="x",
    ylabel="Частота",
    title="График 2. Гистограмма распределения частот заданной ЧП (шаг 50)",
)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(f"{OUT}/График2_Гистограмма.png")

tt = np.linspace(0.1, 1250, 600)
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.hist(x, bins=bins, density=True, alpha=0.55, color="#2f6db5", label="Заданная ЧП")
ax.hist(
    y,
    bins=bins,
    density=True,
    histtype="step",
    lw=1.6,
    color="#e67e22",
    label="Сгенерированная ЧП",
)
ax.plot(
    tt, hypo_pdf(tt), color="#c0392b", lw=2, label="Плотность гипоэкспоненциального закона"
)
ax.plot(
    tt,
    stats.gamma(a=3, scale=m / 3).pdf(tt),
    color="gray",
    ls="--",
    label="Плотность Эрланга 3-го порядка",
)
ax.set(
    xlabel="x",
    ylabel="Плотность",
    title="График 3. Гистограммы и плотность аппроксимирующего закона",
)
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(f"{OUT}/График3_Аппроксимация.png")

fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(i, x, lw=0.9, color="#2f6db5", label="Заданная ЧП")
ax.plot(i, y, lw=0.9, color="#e67e22", alpha=0.85, label="Сгенерированная ЧП")
ax.set(
    xlabel="i",
    ylabel="Значение",
    title="Сравнение заданной и сгенерированной последовательностей",
)
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(f"{OUT}/Сравнение_ЧП.png")

wb = openpyxl.Workbook()
sh = wb.active
sh.title = "Данные"
sh.append(["i", "Заданная ЧП", "Сгенерированная ЧП"])
for j in range(300):
    sh.append([j + 1, float(x[j]), float(y[j])])
for title, src, refd in (("Форма1", R, ref300), ("Форма2", G, R)):
    s2 = wb.create_sheet(title)
    s2.append(["Характеристика", ""] + list(NS))
    for name, kk in (
        ("Мат.ож.", "m"),
        ("Дов.инт.(0,9) +-", 0.9),
        ("Дов.инт.(0,95) +-", 0.95),
        ("Дов.инт.(0,99) +-", 0.99),
        ("Дисперсия", "D"),
        ("С.к.о.", "s"),
        ("К-т вариации", "cv"),
    ):
        s2.append([name, "знач."] + [round(float(src[n][kk]), 4) for n in NS])
        s2.append(
            ["", "%"]
            + [round(float((src[n][kk] - refd[n][kk]) / refd[n][kk] * 100), 2) for n in NS]
        )
s3 = wb.create_sheet("Форма3")
s3.append(["Сдвиг"] + list(range(1, 11)))
s3.append(["АК заданной"] + [round(float(v), 4) for v in ac_x])
s3.append(["АК сгенерир."] + [round(float(v), 4) for v in ac_y])
wb.save(f"{OUT}/УИР1_расчёты.xlsx")
import json

json.dump(
    {
        "x": x.tolist(),
        "y": y.tolist(),
        "R": {str(n): {str(k): float(v) for k, v in R[n].items()} for n in NS},
        "G": {str(n): {str(k): float(v) for k, v in G[n].items()} for n in NS},
        "ac_x": ac_x.tolist(),
        "ac_y": ac_y.tolist(),
        "t1": t1,
        "t2": t2,
        "r_xy": r_xy,
        "lr": [lr.intercept, lr.slope, lr.pvalue],
        "ks": {
            "h": [ks_h.statistic, ks_h.pvalue],
            "e": [ks_e.statistic, ks_e.pvalue],
            "x": [ks_x.statistic, ks_x.pvalue],
            "g": [ks_g.statistic, ks_g.pvalue],
        },
    },
    open(f"{OUT}/results.json", "w"),
    ensure_ascii=False,
)
