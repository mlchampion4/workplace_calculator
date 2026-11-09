import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
import tkinter as tk
from tkinter import ttk, messagebox
import math
from calculations.microclimate import *
from calculations.em_fields import *
from calculations.illuminance import *
from calculations.noise import *
from calculations.psychophysiology import *

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Калькулятор условий труда IT-специалиста (БЖЧ)")
        self.geometry("1050x780")
        self.results = []
        self._build_ui()

    def _build_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=6, pady=6)
        self.vars = {}

        f1 = ttk.Frame(nb); nb.add(f1, text="1. Микроклимат")
        self._row(f1, "Период года:", "period", "combo", ["тёплый", "холодный"], 0)
        self._row(f1, "Температура воздуха, °C:", "temp", "entry", "23", 1)
        self._row(f1, "Отн. влажность, %:", "hum", "entry", "45", 2)
        self._row(f1, "Скорость движения воздуха, м/с:", "airv", "entry", "0.1", 3)
        self._row(f1, "Δ t (воздух − поверхность), °C:", "dtsurf", "entry", "2", 4)

        f2 = ttk.Frame(nb); nb.add(f2, text="2. Освещённость")
        self._row(f2, "Освещённость на рабочем месте, лк:", "lux", "entry", "450", 0)
        self._row(f2, "Коэффициент пульсации, % (колебание яркости за секунду):", "puls", "entry", "5", 1)
        self._row(f2, "Яркость экрана, кд/м²:", "bright", "entry", "150", 2)
        self._row(f2, "Контраст (≥3:1) (отношение яркости к фону):", "contrast", "entry", "3", 3)
        self._row(f2, "Неравномерность (max осв./min осв.):", "uneven", "entry", "3", 4)
        self._row(f2, "КЕО, % (доля естественного света в помещении):", "keo", "entry", "1.0", 5)

        f3 = ttk.Frame(nb); nb.add(f3, text="3. ЭМП от ПЭВМ")
        self._row(f3, "Электростат. потенциал экрана, В (заряд на поверхности монитора):", "esp", "entry", "500", 0)
        self._row(f3, "ЭП 5 Гц–2 кГц, В/м (эл. поле низкой частоты):", "ef_low", "entry", "25", 1)
        self._row(f3, "ЭП 2–400 кГц, В/м (эл. поле высокой частоты):", "ef_high", "entry", "2.5", 2)
        self._row(f3, "МП 5 Гц–2 кГц, нТл (маг. поле низкой частоты):", "mf_low", "entry", "250", 3)
        self._row(f3, "МП 2–400 кГц, нТл (маг. поле высокой частоты):", "mf_high", "entry", "25", 4)
        self._row(f3, "ППЭ СВЧ, мкВт/см² (мощность излучения экрана на его площадь):", "svhf", "entry", "10", 5)
        self._row(f3, "Расстояние до экрана, см:", "dist", "entry", "60", 6)

        f4 = ttk.Frame(nb); nb.add(f4, text="4. Шум")
        self._row(f4, "Уровень звука на рабочем месте, дБА:", "noise", "entry", "50", 0)

        f5 = ttk.Frame(nb); nb.add(f5, text="5. Психофизиология")
        self._row(f5, "Непрерывная работа за экраном, мин:", "cont", "entry", "45", 0)
        self._row(f5, "Суммарное время за экраном, ч/смена:", "hours", "entry", "6", 1)
        self._row(f5, "Монотонность (1–5):", "mono", "entry", "2", 2)
        self._row(f5, "Сверхурочные, ч/год:", "ot_year", "entry", "120", 3)
        self._row(f5, "Переработка, ч/нед:", "ot_week", "entry", "5", 4)

        bar = ttk.Frame(self); bar.pack(fill="x", padx=6)
        ttk.Button(bar, text="Рассчитать", command=self.calculate).pack(side="left", padx=4, pady=4)
        ttk.Button(bar, text="Очистить", command=self.clear).pack(side="left", padx=4, pady=4)

        out = ttk.Frame(self); out.pack(fill="both", expand=True, padx=6, pady=6)
        self.summary = tk.Text(out, height=4, bg="#f0f0f0", font=("Consolas", 10, "bold"))
        self.summary.pack(fill="x")
        cols = ("block", "param", "value", "score", "status", "rec")
        self.tree = ttk.Treeview(out, columns=cols, show="headings", height=18)
        for c, w in zip(cols, (110, 260, 90, 60, 160, 380)):
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=w, anchor="w")
        self.tree.pack(fill="both", expand=True, pady=4)
        vsb = ttk.Scrollbar(out, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.place(relx=1.0, rely=0.18, relheight=0.78, anchor="ne")

    def _row(self, parent, label, key, kind, default, r):
        ttk.Label(parent, text=label).grid(row=r, column=0, sticky="w", padx=6, pady=3)
        if kind == "combo":
            var = tk.StringVar(value=default[0])
            ttk.Combobox(parent, textvariable=var, values=default, state="readonly", width=12).grid(
                row=r, column=1, sticky="w", padx=6, pady=3)
        else:
            var = tk.StringVar(value=str(default))
            ttk.Entry(parent, textvariable=var, width=15).grid(
                row=r, column=1, sticky="w", padx=6, pady=3)
        self.vars[key] = var

    def _f(self, key):
        return float(self.vars[key].get().replace(",", "."))

    def calculate(self):
        self.results = []
        try:
            period = "warm" if self.vars["period"].get() == "тёплый" else "cold"
            self._add("Микроклимат", "Температура воздуха", f"{self._f('temp')} °C",
                      *score_temperature(self._f('temp'), period))
            self._add("Микроклимат", "Отн. влажность", f"{self._f('hum')} %",
                      *score_humidity(self._f('hum')))
            self._add("Микроклимат", "Скорость воздуха", f"{self._f('airv')} м/с",
                      *score_air_speed(self._f('airv')))
            self._add("Микроклимат", "Δt поверхностей", f"{self._f('dtsurf')} °C",
                      *score_surface_temp(self._f('dtsurf')))

            self._add("Освещённость", "Освещённость", f"{self._f('lux')} лк",
                      *score_illuminance(self._f('lux')))
            self._add("Освещённость", "Коэф. пульсации", f"{self._f('puls')} %",
                      *score_pulsation(self._f('puls')))
            self._add("Освещённость", "Яркость экрана", f"{self._f('bright')} кд/м²",
                      *score_brightness(self._f('bright')))
            self._add("Освещённость", "Контраст", f"{self._f('contrast')}:1",
                      *score_contrast(self._f('contrast')))
            self._add("Освещённость", "Неравномерность", f"{self._f('uneven')}",
                      *score_unevenness(self._f('uneven')))
            self._add("Освещённость", "КЕО", f"{self._f('keo')} %",
                      *score_keo(self._f('keo')))

            self._add("ЭМП", "Электростат. потенциал", f"{self._f('esp')} В",
                      *score_esp(self._f('esp')))
            self._add("ЭМП", "ЭП 5 Гц–2 кГц", f"{self._f('ef_low')} В/м",
                      *score_ef_low(self._f('ef_low')))
            self._add("ЭМП", "ЭП 2–400 кГц", f"{self._f('ef_high')} В/м",
                      *score_ef_high(self._f('ef_high')))
            self._add("ЭМП", "МП 5 Гц–2 кГц", f"{self._f('mf_low')} нТл",
                      *score_mf_low(self._f('mf_low')))
            self._add("ЭМП", "МП 2–400 кГц", f"{self._f('mf_high')} нТл",
                      *score_mf_high(self._f('mf_high')))
            self._add("ЭМП", "ППЭ СВЧ", f"{self._f('svhf')} мкВт/см²",
                      *score_svhf(self._f('svhf')))
            self._add("ЭМП", "Расстояние до экрана", f"{self._f('dist')} см",
                      *score_distance(self._f('dist')))

            self._add("Шум", "Уровень звука", f"{self._f('noise')} дБА",
                      *score_noise(self._f('noise')))

            self._add("Психофизиология", "Непрерывная работа", f"{self._f('cont')} мин",
                      *score_continuous_minutes(self._f('cont')))
            self._add("Психофизиология", "Время за экраном", f"{self._f('hours')} ч",
                      *score_screen_hours(self._f('hours')))
            self._add("Психофизиология", "Монотонность", f"{self._f('mono')}",
                      *score_monotony(self._f('mono')))
            self._add("Психофизиология", "Сверхурочные", f"{self._f('ot_year')} ч/год",
                      *score_overtime_hours(self._f('ot_year')))
            self._add("Психофизиология", "Переработка", f"{self._f('ot_week')} ч/нед",
                      *score_overtime_week(self._f('ot_week')))

        except ValueError:
            messagebox.showerror("Ошибка", "Проверьте ввод: все значения должны быть числами.")
            return

        self._render()

    def _add(self, block, param, value, score, status, rec):
        self.results.append((block, param, value, score, status, rec))

    def _render(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for r in self.results:
            self.tree.insert("", "end", values=r)

        total = sum(r[3] for r in self.results)
        critical = sum(1 for r in self.results if r[3] >= 3)
        bad = sum(1 for r in self.results if r[3] == 2)
        warns = sum(1 for r in self.results if r[3] == 1)
        n = len(self.results)
        max_possible = 3 * n

        if critical:
            cat = "ОПАСНЫЙ (критический) — устранить немедленно"
        elif bad >= 5:
            cat = "ВРЕДНЫЙ 2 степени — требуется план улучшений"
        elif bad >= 1:
            cat = "ВРЕДНЫЙ 1 степени — корректировка условий"
        elif warns >= 3:
            cat = "ДОПУСТИМЫЙ — есть отклонения"
        else:
            cat = "ОПТИМАЛЬНЫЙ"

        text = (
            f"ИТОГО: {total} баллов из {max_possible}  |  "
            f"Критично: {critical}  Вредно: {bad}  Допустимо: {warns}  "
            f"Норма: {n - critical - bad - warns}\n"
            f"КАТЕГОРИЯ УСЛОВИЙ ТРУДА: {cat}\n"
            f"Приоритетные рекомендации:\n"
        )
        recs = [r[5] for r in self.results if r[3] >= 1 and r[5]]
        text += "\n".join(f"  • {x}" for x in recs[:8]) if recs else "  • Существенных замечаний нет."
        self.summary.delete("1.0", "end")
        self.summary.insert("1.0", text)

    def clear(self):
        for k, v in self.vars.items():
            if k == "period":
                v.set("тёплый")
        self.results = []
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.summary.delete("1.0", "end")
