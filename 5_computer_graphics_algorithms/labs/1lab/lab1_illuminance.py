
import math
from dataclasses import dataclass

import numpy as np
from PIL import Image

MM_TO_M = 1e-3

LIMITS = {
    "W": (100.0, 10000.0),
    "H": (100.0, 10000.0),
    "Wres": (200, 800),
    "Hres": (200, 800),
    "xL": (-10000.0, 10000.0),
    "yL": (-10000.0, 10000.0),
    "zL": (100.0, 10000.0),
    "I0": (0.01, 10000.0),
}


@dataclass
class Params:
    W: float = 5000.0
    H: float = 4000.0
    Wres: int = 500
    Hres: int = 400
    xL: float = 500.0
    yL: float = -700.0
    zL: float = 2000.0
    I0: float = 1000.0
    xC: float = 0.0
    yC: float = 0.0
    R: float = 1800.0


def square_pixel(p: Params):
    a = max(p.W / p.Wres, p.H / p.Hres)
    return a, p.Wres * a, p.Hres * a


def validate(p: Params) -> list:
    errors = []
    for key in ("W", "H", "Wres", "Hres", "xL", "yL", "zL", "I0"):
        lo, hi = LIMITS[key]
        v = getattr(p, key)
        if not (lo <= v <= hi):
            errors.append(f"{key} = {v:g} вне диапазона [{lo:g}; {hi:g}]")
    for key in ("Wres", "Hres"):
        if not float(getattr(p, key)).is_integer():
            errors.append(f"{key} должно быть целым")
    if p.R <= 0:
        errors.append("Радиус R должен быть больше 0")
    if not errors:
        _, w_eff, h_eff = square_pixel(p)
        if not (-h_eff / 2 <= p.xC <= h_eff / 2 and -w_eff / 2 <= p.yC <= w_eff / 2):
            errors.append("Центр круга (xC, yC) должен лежать внутри области изображения")
    return errors


def illuminance(x_mm, y_mm, p: Params):
    dx = (np.asarray(x_mm, dtype=float) - p.xL) * MM_TO_M
    dy = (np.asarray(y_mm, dtype=float) - p.yL) * MM_TO_M
    dz = p.zL * MM_TO_M
    r2 = dx * dx + dy * dy + dz * dz
    r = np.sqrt(r2)
    cos_theta = dz / r          # угол от оси источника
    cos_alpha = dz / r          # угол от нормали к плоскости
    intensity = p.I0 * cos_theta
    return intensity * cos_alpha / r2


@dataclass
class Result:
    Hres: int
    pix: float
    W_eff: float
    H_eff: float
    x: np.ndarray
    y: np.ndarray
    E: np.ndarray
    mask: np.ndarray
    image: np.ndarray
    E_max: float


def compute(p: Params) -> Result:
    errors = validate(p)
    if errors:
        raise ValueError("\n".join(errors))

    pix, W_eff, H_eff = square_pixel(p)
    Hres = p.Hres

    y = -W_eff / 2 + (np.arange(p.Wres) + 0.5) * pix
    x = -H_eff / 2 + (np.arange(Hres) + 0.5) * pix
    X, Y = np.meshgrid(x, y, indexing="ij")

    E = illuminance(X, Y, p)
    mask = (X - p.xC) ** 2 + (Y - p.yC) ** 2 <= p.R ** 2
    if not mask.any():
        raise ValueError("В круг не попал ни один пиксель — увеличьте R "
                         "или разрешение.")

    E_in = E[mask]
    E_max = float(E_in.max())

    image = np.zeros_like(E, dtype=np.uint8)
    image[mask] = np.clip(np.rint(E_in / E_max * 255.0), 0, 255).astype(np.uint8)


    return Result(Hres=Hres, pix=pix, W_eff=W_eff, H_eff=H_eff, x=x, y=y, E=E, mask=mask,
                  image=image, E_max=E_max)


def save_image(res: Result, path: str):
    Image.fromarray(res.image, mode="L").save(path)


def draw_image(ax, p: Params, res: Result, overlay=True):
    ax.clear()
    extent = (-res.W_eff / 2, res.W_eff / 2, res.H_eff / 2, -res.H_eff / 2)
    ax.imshow(res.image, cmap="gray", vmin=0, vmax=255, extent=extent,
              interpolation="nearest")
    ax.set_xlabel("Y, мм")
    ax.set_ylabel("X, мм")
    ax.set_title(f"Распределение освещённости ({p.Wres}×{res.Hres}, 0–255)")
    if overlay:
        ax.axhline(p.xC, color="tab:orange", lw=0.8, ls="--")
        ax.axvline(p.yC, color="tab:cyan", lw=0.8, ls="--")
        ax.plot(p.yL, p.xL, marker="*", color="yellow", mec="k", ms=11,
                ls="none", label="проекция источника")
        if ax.get_legend_handles_labels()[0]:
            ax.legend(loc="lower right", fontsize=7, framealpha=0.8)
        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])


def _interp_index(coords: np.ndarray, value: float):
    t = (value - coords[0]) / (coords[1] - coords[0])
    t = min(max(t, 0.0), len(coords) - 1.0)
    i = min(int(math.floor(t)), len(coords) - 2)
    return i, t - i


def section_profiles(p: Params, res: Result):
    i, wi = _interp_index(res.x, p.xC)
    row_E = (1 - wi) * res.E[i, :] + wi * res.E[i + 1, :]
    row_E = np.where((res.y - p.yC) ** 2 <= p.R ** 2, row_E, np.nan)

    j, wj = _interp_index(res.y, p.yC)
    col_E = (1 - wj) * res.E[:, j] + wj * res.E[:, j + 1]
    col_E = np.where((res.x - p.xC) ** 2 <= p.R ** 2, col_E, np.nan)
    return row_E, col_E


def draw_sections(ax, p: Params, res: Result):
    ax.clear()
    row_E, col_E = section_profiles(p, res)
    ax.plot(res.y, row_E, color="tab:orange", lw=1.6,
            label=f"вдоль оси Y (X = {p.xC:g} мм)")
    ax.plot(res.x, col_E, color="tab:cyan", lw=1.6,
            label=f"вдоль оси X (Y = {p.yC:g} мм)")
    ax.set_xlabel("координата вдоль сечения, мм")
    ax.set_ylabel("E, Вт/м²")
    ax.set_title("Сечения через центр круга")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="lower center")
    ax.set_ylim(bottom=0)

    e_max = res.E_max
    sec = ax.secondary_yaxis("right", functions=(lambda e: e / e_max * 255.0,
                                                 lambda v: v / 255.0 * e_max))
    sec.set_ylabel("значение пикселя (0–255)")


BG = "#000000"
BG_FIELD = "#141414"
BG_BTN = "#262626"
BG_BTN_ACTIVE = "#3a3a3a"
FG = "#e6e6e6"
FG_DIM = "#8a8a8a"
EDGE = "#555555"


def apply_dark_theme():
    import matplotlib
    matplotlib.rcParams.update({
        "figure.facecolor": BG, "figure.edgecolor": BG,
        "axes.facecolor": BG, "axes.edgecolor": EDGE,
        "axes.labelcolor": FG, "axes.titlecolor": FG,
        "text.color": FG,
        "xtick.color": FG, "ytick.color": FG,
        "grid.color": "#777777",
        "legend.facecolor": "#111111", "legend.edgecolor": EDGE,
        "legend.labelcolor": FG,
        "savefig.facecolor": BG, "savefig.edgecolor": BG,
    })


def save_sections_plot(p: "Params", res: "Result", path: str, dpi=130):
    from matplotlib.figure import Figure
    fig = Figure(figsize=(9, 5), dpi=dpi)
    draw_sections(fig.add_subplot(1, 1, 1), p, res)
    fig.tight_layout()
    fig.savefig(path)


def run_gui(p0: Params):
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    apply_dark_theme()
    root = tk.Tk()
    root.title("Освещённость от точечного ламбертовского источника")
    root.geometry("1400x860")
    root.configure(bg=BG)

    st = ttk.Style(root)
    st.theme_use("clam")
    st.configure(".", background=BG, foreground=FG, fieldbackground=BG_FIELD,
                 bordercolor=EDGE, lightcolor=BG, darkcolor=BG, troughcolor=BG)
    st.configure("TFrame", background=BG)
    st.configure("TLabel", background=BG, foreground=FG)
    st.configure("Hint.TLabel", background=BG, foreground=FG_DIM)
    st.configure("TEntry", fieldbackground=BG_FIELD, foreground=FG,
                 insertcolor=FG, bordercolor=EDGE)
    st.configure("TButton", background=BG_BTN, foreground=FG, bordercolor=EDGE,
                 focuscolor=BG_BTN, padding=4)
    st.map("TButton", background=[("active", BG_BTN_ACTIVE), ("pressed", BG_BTN_ACTIVE)])
    st.configure("TCheckbutton", background=BG, foreground=FG, indicatorbackground=BG_FIELD,
                 indicatorforeground=FG, focuscolor=BG)
    st.map("TCheckbutton", background=[("active", BG)],
           indicatorbackground=[("selected", BG_BTN_ACTIVE)])

    state = {"res": None, "p": None}

    left = ttk.Frame(root, padding=8)
    left.pack(side="left", fill="y")

    fields = [
        ("Область изображения", None, None),
        ("W — ширина, мм", "W", "100 … 10000"),
        ("H — высота, мм", "H", "100 … 10000"),
        ("Разрешение", None, None),
        ("Wres, пикс", "Wres", "200 … 800"),
        ("Hres, пикс", "Hres", "200 … 800"),
        ("Источник света", None, None),
        ("xL, мм", "xL", "±10000"),
        ("yL, мм", "yL", "±10000"),
        ("zL, мм", "zL", "100 … 10000"),
        ("I0, Вт/ср", "I0", "0.01 … 10000"),
        ("Круг расчёта", None, None),
        ("xC, мм", "xC", "внутри области"),
        ("yC, мм", "yC", "внутри области"),
        ("R, мм", "R", "> 0"),
    ]
    vars_ = {}
    pix_info = tk.StringVar()
    row = 0
    for label, key, hint in fields:
        if key is None:
            ttk.Label(left, text=label, font=("TkDefaultFont", 10, "bold")).grid(
                row=row, column=0, columnspan=3, sticky="w", pady=(10, 2))
        else:
            ttk.Label(left, text=label).grid(row=row, column=0, sticky="w")
            v = tk.StringVar()
            e = ttk.Entry(left, textvariable=v, width=11)
            e.grid(row=row, column=1, padx=4, pady=1)
            v.set(f"{getattr(p0, key):g}")
            e.bind("<Return>", lambda _e: on_compute())
            ttk.Label(left, text=hint, style="Hint.TLabel").grid(row=row, column=2, sticky="w")
            vars_[key] = v
        row += 1
        if key == "Hres":
            ttk.Label(left, textvariable=pix_info, style="Hint.TLabel",
                      justify="left").grid(row=row, column=0, columnspan=3, sticky="w")
            row += 1

    def read_params() -> Params:
        vals = {}
        for key in ("W", "H", "Wres", "Hres", "xL", "yL", "zL", "I0", "xC", "yC", "R"):
            s = vars_[key].get().strip().replace(",", ".")
            try:
                vals[key] = float(s)
            except ValueError:
                raise ValueError(f"Параметр {key}: «{s}» — не число")
        for key in ("Wres", "Hres"):
            vals[key] = int(round(vals[key]))
        return Params(**vals)

    def update_pix_info(*_):
        # Показывает скорректированный квадратный пиксель и фактическую область
        try:
            p = read_params()
            if min(p.W, p.H, p.Wres, p.Hres) <= 0:
                raise ValueError
            a, w_eff, h_eff = square_pixel(p)
            raw_w, raw_h = p.W / p.Wres, p.H / p.Hres
            fixed = abs(raw_w - raw_h) >= 1e-9 * max(raw_w, raw_h)
            pix_info.set(
                f"Пиксель: {a:g} × {a:g} мм" + (" (скорректирован)" if fixed else "") + "\n"
                + (f"W/Wres = {raw_w:.6g}, H/Hres = {raw_h:.6g} мм\n" if fixed else "")
                + f"Фактическая область: {w_eff:g} × {h_eff:g} мм")
        except Exception:
            pix_info.set("Пиксель: —")

    for k in ("W", "H", "Wres", "Hres"):
        vars_[k].trace_add("write", update_pix_info)
    update_pix_info()

    overlay_var = tk.BooleanVar(value=True)

    btns = ttk.Frame(left)
    btns.grid(row=row, column=0, columnspan=3, pady=(14, 4), sticky="ew")
    row += 1
    ttk.Checkbutton(left, text="Показывать линии сечений и источник",
                    variable=overlay_var, command=lambda: redraw()).grid(
        row=row, column=0, columnspan=3, sticky="w")
    row += 1

    fig = Figure(figsize=(9, 8), dpi=100)
    ax_img = fig.add_subplot(2, 1, 1)
    ax_sec = fig.add_subplot(2, 1, 2)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().configure(bg=BG, highlightthickness=0)
    canvas.get_tk_widget().pack(side="right", fill="both", expand=True)

    def redraw():
        res, p = state["res"], state["p"]
        if res is None:
            return
        draw_image(ax_img, p, res, overlay=overlay_var.get())
        draw_sections(ax_sec, p, res)
        fig.tight_layout()
        canvas.draw()

    def on_compute():
        try:
            p = read_params()
            res = compute(p)
        except ValueError as ex:
            messagebox.showerror("Ошибка параметров", str(ex))
            return
        state["res"], state["p"] = res, p
        vars_["Wres"].set(str(p.Wres))
        vars_["Hres"].set(str(p.Hres))
        redraw()

    def on_save_image():
        if state["res"] is None:
            on_compute()
            if state["res"] is None:
                return
        path = filedialog.asksaveasfilename(
            defaultextension=".png", initialfile="illuminance.png",
            filetypes=[("PNG", "*.png"), ("BMP", "*.bmp"), ("TIFF", "*.tif")])
        if path:
            save_image(state["res"], path)
            messagebox.showinfo("Сохранено", f"Изображение записано:\n{path}")

    def on_save_plot():
        if state["res"] is None:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png", initialfile="sections.png",
            filetypes=[("PNG", "*.png")])
        if path:
            save_sections_plot(state["p"], state["res"], path)

    ttk.Button(btns, text="Рассчитать", command=on_compute).pack(fill="x", pady=1)
    ttk.Button(btns, text="Сохранить изображение…", command=on_save_image).pack(fill="x", pady=1)
    ttk.Button(btns, text="Сохранить график сечений…", command=on_save_plot).pack(fill="x", pady=1)

    on_compute()
    root.mainloop()


if __name__ == "__main__":
    run_gui(Params())
