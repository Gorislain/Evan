"""
Расчёт характеристик I-V модуля
===============================

Примеры моделирования характеристик I-V с использованием эквивалентной модели одно-диодной цепи.
"""

from pvlib import pvsystem
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Пример параметров модуля для Canadian Solar CS5P-220M:
parameters = {
    'Name': 'Canadian Solar CS5P-220M',
    'BIPV': 'N',
    'Date': '10/5/2009',
    'T_NOCT': 42.4,
    'A_c': 1.7,
    'N_s': 96,
    'I_sc_ref': 5.1,
    'V_oc_ref': 59.4,
    'I_mp_ref': 4.69,
    'V_mp_ref': 46.9,
    'alpha_sc': 0.004539,
    'beta_oc': -0.22216,
    'a_ref': 2.6373,
    'I_L_ref': 5.114,
    'I_o_ref': 8.196e-10,
    'R_s': 1.065,
    'R_sh_ref': 381.68,
    'Adjust': 8.7,
    'gamma_r': -0.476,
    'Version': 'MM106',
    'PTC': 200.1,
    'Technology': 'Mono-c-Si',
}

cases = [
    (1000, 50),
    (1000, 40),
    (1000, 30),
    (400, 50),
    (400, 40),
    (400, 30)
]

conditions = pd.DataFrame(cases, columns=['Geff', 'Tcell'])

# Корректировка параметров по условиям работы
# с использованием модели De Soto:
IL, I0, Rs, Rsh, nNsVth = pvsystem.calcparams_desoto(
    conditions['Geff'],
    conditions['Tcell'],
    alpha_sc=parameters['alpha_sc'],
    a_ref=parameters['a_ref'],
    I_L_ref=parameters['I_L_ref'],
    I_o_ref=parameters['I_o_ref'],
    R_sh_ref=parameters['R_sh_ref'],
    R_s=parameters['R_s'],
    EgRef=1.121,
    dEgdT=-0.0002677
)

# Подставляем параметры в уравнение SDE и решаем для характеристик I-V:
curve_info = pvsystem.singlediode(
    photocurrent=IL,
    saturation_current=I0,
    resistance_series=Rs,
    resistance_shunt=Rsh,
    nNsVth=nNsVth,
    method='lambertw'
)

# Просмотр структуры curve_info
print("curve_info columns:", curve_info.columns)
print("curve_info head:\n", curve_info.head())

# Инициализация списков для хранения данных
voltage_arrays = []
current_arrays = []

# Извлечение массивов напряжения и тока для каждого случая
for i, case in conditions.iterrows():
    # Доступ к столбцам по их реальным именам
    voltage = curve_info.iloc[i]['v']
    current = curve_info.iloc[i]['i']
    voltage_arrays.append(voltage)
    current_arrays.append(current)

# Преобразуем списки в numpy массивы при необходимости
voltage_arrays = np.array(voltage_arrays)
current_arrays = np.array(current_arrays)

# Печать массивов
for i, case in conditions.iterrows():
    print(f"Условие {i+1}: Geff={case['Geff']} W/m^2, Tcell={case['Tcell']} C")
    print(f"Массив напряжений: {voltage_arrays[i]}")
    print(f"Массив токов: {current_arrays[i]}")

# Построение графиков расчётных кривых:
plt.figure()
for i, case in conditions.iterrows():
    label = (
        "$G_{eff}$ " + f"{case['Geff']} $W/m^2$\n"
        "$T_{cell}$ " + f"{case['Tcell']} $C$"
    )
    plt.plot(voltage_arrays[i], current_arrays[i], label=label)
    v_mp = curve_info['v_mp'][i]
    i_mp = curve_info['i_mp'][i]
    # Отметим точку максимальной мощности
    plt.plot([v_mp], [i_mp], 'ok')

plt.xlabel('Напряжение модуля [V]')
plt.ylabel('Ток модуля [A]')
plt.title(parameters['Name'])
plt.legend(loc='best')
plt.show()

# Стрелки тренда 
def draw_arrow(ax, label, x0, y0, rotation, size, direction):
    style = direction + 'arrow'
    bbox_props = dict(boxstyle=style, fc=(0.8, 0.9, 0.9), ec="b", lw=1)
    t = ax.text(x0, y0, label, ha="left", va="bottom", rotation=rotation,
                size=size, bbox=bbox_props, zorder=-1)

    bb = t.get_bbox_patch()
    bb.set_boxstyle(style, pad=0.6)

ax = plt.gca()
draw_arrow(ax, 'Иррадиация', 20, 2.5, 90, 15, 'r')
draw_arrow(ax, 'Температура', 35, 1, 0, 15, 'l')

plt.show()

# Вывод сводки параметров I-V кривых
print(pd.DataFrame({
    'i_sc': curve_info['i_sc'],
    'v_oc': curve_info['v_oc'],
    'i_mp': curve_info['i_mp'],
    'v_mp': curve_info['v_mp'],
    'p_mp': curve_info['p_mp'],
}))
