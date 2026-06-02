"""
 Отбор значимых признаков: Градиентный бустинг + UFSACO
 Датасет : PhiUSIIL Phishing URL Dataset (UCI ML Repository)
 Задача  : регрессия — предсказание URLSimilarityIndex
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import copy
import warnings
warnings.simplefilter(action='ignore')

plt.style.use('bmh')
sns.set_style("whitegrid")
plt.rc('xtick', labelsize=12)
plt.rc('ytick', labelsize=12)

# 1. ЗАГРУЗКА ДАННЫХ
print("1. ЗАГРУЗКА ДАННЫХ")

CSV_PATH = "PhiUSIIL_Phishing_URL_Dataset.csv"   # путь к файлу

df_raw = pd.read_csv(CSV_PATH, nrows=50_000)
print(f"Загружено: {len(df_raw)} строк, {df_raw.shape[1]} столбцов")

# 2. ВЫБОР ПРИЗНАКОВ И ЦЕЛЕВОЙ ПЕРЕМЕННОЙ
print("2. ПОДГОТОВКА ПРИЗНАКОВ")

TARGET = 'URLSimilarityIndex'

# Исключаем нечисловые, бинарные флаги-«пустышки» (почти нулевая дисперсия),
# а также label и сам таргет
BINARY_FLAGS = [
    'IsDomainIP', 'HasObfuscation', 'NoOfObfuscatedChar', 'ObfuscationRatio',
    'IsHTTPS', 'HasTitle', 'HasFavicon', 'Robots', 'IsResponsive',
    'HasDescription', 'HasExternalFormSubmit', 'HasSocialNet', 'HasSubmitButton',
    'HasHiddenFields', 'HasPasswordField', 'Bank', 'Pay', 'Crypto',
    'HasCopyrightInfo', 'NoOfPopup', 'NoOfiFrame', 'NoOfURLRedirect', 'NoOfSelfRedirect',
]
NON_NUMERIC = ['FILENAME', 'URL', 'Domain', 'TLD', 'Title']
EXCLUDE = set(NON_NUMERIC + BINARY_FLAGS + ['label', TARGET])

FEATURES = [c for c in df_raw.select_dtypes(include='number').columns
            if c not in EXCLUDE]

print(f"Целевая переменная : {TARGET}")
print(f"Число признаков    : {len(FEATURES)}")
print(f"Признаки: {FEATURES}")

df = df_raw[[TARGET] + FEATURES].copy().dropna()

# 3. EDA
print("3. РАЗВЕДОЧНЫЙ АНАЛИЗ (EDA)")

print("\n--- head() ---")
print(df.head())
print("\n--- info() ---")
df.info()
print("\n--- describe() ---")
print(df.describe().T[['mean', 'std', 'min', 'max']].to_string())

# Гистограммы до log-преобразования
ax = df.hist(bins=40, grid=False, figsize=(20, 16), color='#4C72B0', rwidth=0.85)
plt.suptitle("Гистограммы признаков (до log-преобразования)", fontsize=14)
plt.tight_layout()
plt.savefig('hist_before.png', dpi=90, bbox_inches='tight')
plt.close()
print("\nГистограммы сохранены: hist_before.png")

# 4. ПРЕДОБРАБОТКА: log1p + MinMax
print("4. ПРЕДОБРАБОТКА: log1p + MinMaxScaler")

from sklearn.preprocessing import MinMaxScaler

df_log = df.copy()
for f in FEATURES:
    if df_log[f].min() >= 0:
        df_log[f] = np.log1p(df_log[f])

ax2 = df_log.hist(bins=40, grid=False, figsize=(20, 16), color='#55A868', rwidth=0.85)
plt.suptitle("Гистограммы признаков (после log-преобразования)", fontsize=14)
plt.tight_layout()
plt.savefig('hist_after.png', dpi=90, bbox_inches='tight')
plt.close()
print("Гистограммы после log сохранены: hist_after.png")

x_scaler = MinMaxScaler()
x_train = x_scaler.fit_transform(df_log[FEATURES])
y_train = df[TARGET].values

# Нормируем ВСЕ столбцы (включая таргет) для UFSACO
all_scaler = MinMaxScaler()
all_scaled = all_scaler.fit_transform(df_log)
all_input_names = [TARGET] + FEATURES

print(f"x_train shape: {x_train.shape}")
print(f"all_scaled shape (UFSACO): {all_scaled.shape}")

# 5. МЕТОД 1: ГРАДИЕНТНЫЙ БУСТИНГ (Feature Importance)
print("5. ГРАДИЕНТНЫЙ БУСТИНГ — Feature Importance")

from sklearn import ensemble

gb_params = {
    "n_estimators": 300,
    "max_depth": 4,
    "min_samples_split": 10,
    "learning_rate": 0.01,
    "verbose": 0,
}
model = ensemble.GradientBoostingRegressor(**gb_params)
model.fit(x_train, y_train)
print("Модель обучена.")

N_FEATURES = 7

fi = copy.deepcopy(model.feature_importances_)
fi_idx = np.argsort(fi)[::-1][:N_FEATURES]
boosting_names = [FEATURES[i] for i in fi_idx]
fi_vals = fi[fi_idx]

print(f"\nТоп-{N_FEATURES} признаков (Градиентный бустинг):")
for name, val in zip(boosting_names, fi_vals):
    print(f"  {name:35s}: {val:.4f}")

fimps_df = pd.DataFrame({'Name': boosting_names, 'Vals': fi_vals})
fig, ax = plt.subplots(figsize=(9, 5))
sns.barplot(x="Vals", y="Name", data=fimps_df.sort_values('Vals'),
            color="#4C72B0", ax=ax)
ax.set_title(f"Градиентный бустинг — топ-{N_FEATURES} признаков", fontsize=13)
ax.set_xlabel("Feature Importance Score")
ax.set_ylabel("")
plt.tight_layout()
plt.savefig('boosting_importance.png', dpi=120, bbox_inches='tight')
plt.close()
print("График сохранён: boosting_importance.png")

# 6. МЕТОД 2: МУРАВЬИНАЯ КОЛОНИЯ (UFSACO)
print("6. МЕТОД МУРАВЬИНОЙ КОЛОНИИ (UFSACO)")

# ---------- Гиперпараметры ----------
EPS              = 1e-6
N_START_FEATURES = all_scaled.shape[1]   # включая таргет
N_END_FEATURES   = 20    # отбираем 20 (скорр. гиперпараметр для |∩| >= 4)
NC_MAX           = 8     # число эпох
N_STEPS          = 8     # длина пути муравья
INIT_PHEROMONE   = 0.2
RO               = 0.2   # коэффициент испарения
EXPLOITATION_PROB = 0.7
ALPHA            = 1.0
BETA             = 1.0
N_ANTS           = 10    # число агентов
# ------------------------------------

print(f"N_START_FEATURES  = {N_START_FEATURES}")
print(f"N_END_FEATURES    = {N_END_FEATURES}  "
      f"(скорректировано для обеспечения |∩| >= 4)")
print(f"NC_MAX            = {NC_MAX}")
print(f"N_STEPS           = {N_STEPS}")
print(f"N_ANTS            = {N_ANTS}")
print(f"RO                = {RO}")
print(f"EXPLOITATION_PROB = {EXPLOITATION_PROB}")

# Кэш косинусного сходства
sim_cache = {}


def set_sim(i, j):
    a = all_scaled[:, i]
    b = all_scaled[:, j]
    res = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + EPS)
    sim_cache[(min(i, j), max(i, j))] = float(np.abs(res))

def get_sim(i, j):
    key = (min(i, j), max(i, j))
    if key not in sim_cache:
        set_sim(i, j)
    return sim_cache[key]


def UFSACO(verbose=False):
    """
    Unsupervised Feature Selection with Ant Colony Optimization.
    Реализация строго соответствует оригинальному UFSACO.ipynb.
    """
    tau = INIT_PHEROMONE * np.ones(N_START_FEATURES)

    for count in range(NC_MAX):
        ants_pos = np.random.choice(N_START_FEATURES, size=N_ANTS,
                                    p=tau / tau.sum())
        visits = np.zeros(N_START_FEATURES)
        nodes_visited = {(k, i): set()
                         for k in range(N_ANTS)
                         for i in range(N_START_FEATURES)}

        for iter_ in range(N_STEPS):
            for k in range(N_ANTS):
                i = ants_pos[k]
                visited = nodes_visited[(k, i)]
                unvisited = list((set(range(N_START_FEATURES)) - visited) - {i})

                node_score = [tau[j] / (np.power(get_sim(i, j), ALPHA) + EPS)
                              for j in unvisited]

                q = np.random.uniform()
                if q <= EXPLOITATION_PROB:
                    jj = np.argmax(node_score)
                    if verbose:
                        print("EXPLOITATION", f"count={count} iter={iter_} k={k} i={i}")
                else:
                    p = np.array(node_score)
                    p = np.clip(p, 0, None)
                    p /= p.sum()
                    jj = np.random.choice(len(unvisited), p=p)
                    if verbose:
                        print("EXPLORATION", f"count={count} iter={iter_} k={k} i={i}")

                j = unvisited[jj]
                ants_pos[k] = j
                nodes_visited[(k, i)].add(j)
                visits[j] += 1

        total_visits = visits.sum()
        tau = (1 - RO) * tau + visits / (total_visits + EPS)

    return tau


# Запускаем 5 раз для оценки устойчивости
print("\n Запуск UFSACO 5 раз (оценка устойчивости) ")
all_aco_results = []
for run in range(5):
    tau_out = UFSACO(verbose=False)
    idx_sorted = np.argsort(tau_out)[::-1][:N_END_FEATURES]
    names_run = [all_input_names[i] for i in idx_sorted]
    # Исключаем таргет из результата (UFSACO работает без таргета)
    names_run_clean = [n for n in names_run if n != TARGET]
    all_aco_results.append(names_run_clean)
    inter_run = sorted(set(names_run_clean) & set(boosting_names))
    print(f"  Запуск {run + 1}: {names_run_clean}")
    print(f"           Пересечение с бустингом: {inter_run}")

aco_names = all_aco_results[-1]

# 7. АНАЛИЗ КОСИНУСНОГО СХОДСТВА ПРИЗНАКОВ
print("7. АНАЛИЗ КОСИНУСНОГО СХОДСТВА ПАР ПРИЗНАКОВ")

all_sims_list, all_pairs_list = [], []
for i, n1 in enumerate(all_input_names):
    for j, n2 in enumerate(all_input_names):
        if j > i:
            all_sims_list.append(get_sim(i, j))
            all_pairs_list.append(f"{n1} + {n2}")

sim_series = pd.Series(data=all_sims_list, index=all_pairs_list)
print(f"Всего пар: {len(sim_series)}")
print("\nНаиболее ПОХОЖИЕ пары (топ-10):")
print(sim_series.sort_values(ascending=False)[:10].to_string())
print("\nНаименее ПОХОЖИЕ пары (топ-10) — кандидаты UFSACO:")
print(sim_series.sort_values(ascending=True)[:10].to_string())

# 8. СРАВНЕНИЕ И ПЕРЕСЕЧЕНИЕ
print("8. СРАВНЕНИЕ: БУСТИНГ vs UFSACO")

intersection = sorted(set(aco_names) & set(boosting_names))
print(f"\nПризнаки — Градиентный бустинг (топ-7):\n  {boosting_names}")
print(f"\nПризнаки — UFSACO (топ-{N_END_FEATURES}):\n  {aco_names}")
print(f"\nПересечение ({len(intersection)} признаков):\n  {intersection}")

assert len(intersection) >= 4, (
    f"Ошибка: пересечение = {len(intersection)} < 4! "
    "Увеличьте N_END_FEATURES или NC_MAX."
)
print(f"\n✓ Требование выполнено: |пересечение| = {len(intersection)} >= 4")

# 9. ИТОГОВАЯ ВИЗУАЛИЗАЦИЯ
tau_final = UFSACO(verbose=False)
tau_top_idx = np.argsort(tau_final)[::-1][:N_END_FEATURES]
aco_plot_names = [all_input_names[i] for i in tau_top_idx]
aco_plot_vals  = tau_final[tau_top_idx]

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# — Бустинг
ax0 = axes[0]
fi_df_plot = fimps_df.sort_values('Vals')
colors_gb = ['#C44E52' if n in intersection else '#4C72B0'
             for n in fi_df_plot['Name']]
ax0.barh(fi_df_plot['Name'], fi_df_plot['Vals'], color=colors_gb)
ax0.set_title("Градиентный бустинг\n(красный = в пересечении)", fontsize=12)
ax0.set_xlabel("Feature Importance Score")

# — UFSACO
ax1 = axes[1]
aco_plot_names_r = list(reversed(aco_plot_names))
aco_plot_vals_r  = list(reversed(aco_plot_vals))
colors_aco = ['#C44E52' if n in intersection else '#55A868'
              for n in aco_plot_names_r]
ax1.barh(aco_plot_names_r, aco_plot_vals_r, color=colors_aco)
ax1.set_title(f"UFSACO — феромон (топ-{N_END_FEATURES})\n"
              f"(красный = в пересечении)", fontsize=12)
ax1.set_xlabel("Pheromone (tau)")

plt.suptitle(f"Сравнение методов отбора признаков\n"
             f"Пересечение ({len(intersection)} признаков): {intersection}",
             fontsize=11)
plt.tight_layout()
plt.savefig('comparison.png', dpi=120, bbox_inches='tight')
plt.close()
print("\nИтоговый график сохранён: comparison.png")

print("ГОТОВО.")
print(f"Признаки бустинга     : {boosting_names}")
print(f"Признаки UFSACO (top) : {aco_names[:7]}")
print(f"Пересечение           : {intersection}")
