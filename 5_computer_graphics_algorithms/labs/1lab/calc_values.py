"""
Запуск:  
python calc_values.py variant.json values_report.txt
"""
import json
import sys

from lab1_illuminance import Params, compute, illuminance


def fmt_real(v: float) -> str:
    return f"{v:.6f}" if abs(v) >= 1e-3 else f"{v:.6e}"


def main(variant_path="variant.json", out_path="values_report.txt"):
    with open(variant_path, encoding="utf-8") as f:
        data = json.load(f)

    p = Params(**data["params"])
    res = compute(p)

    lines = [
        "Расчётные значения освещённости, Вт/м²",
        f"Область W×H = {p.W:g}×{p.H:g} мм, разрешение {p.Wres}×{p.Hres}, "
        f"пиксель {res.pix:g}×{res.pix:g} мм",
        f"Источник L = ({p.xL:g}; {p.yL:g}; {p.zL:g}) мм, I0 = {p.I0:g} Вт/ср",
        f"Круг: центр ({p.xC:g}; {p.yC:g}) мм, R = {p.R:g} мм",
        "",
        "Освещённость в пяти точках:",
    ]
    for pt in data["points"]:
        e = float(illuminance(pt["x"], pt["y"], p))
        lines.append(f"  {pt['name']:<28s} ({pt['x']:g}; {pt['y']:g})".ljust(46)
                     + fmt_real(e))

    e_in = res.E[res.mask]
    lines += [
        "",
        f"В пределах круга ({int(res.mask.sum())} пикселей):",
        f"  Максимум  {fmt_real(float(e_in.max()))}",
        f"  Минимум   {fmt_real(float(e_in.min()))}",
        f"  Среднее   {fmt_real(float(e_in.mean()))}",
    ]

    text = "\n".join(lines)
    print(text)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:3])
