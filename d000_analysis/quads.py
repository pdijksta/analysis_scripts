import numpy as np
import matplotlib.pyplot as plt
import itertools

from pyecloud_device import pyecloud_device
from simulation_parameters import *

# DEFINE
MIN, MAX = 0, 1

one_list = np.ones_like(sey_list)
pyecloud_device_easy = lambda device, coast_str: pyecloud_device(device, coast_str, devices, coast_strs, hl_pyecloud)

# intersection points
inters_array = np.ones(shape=(len(quads), len(coast_strs), 2))
inters_array[:,:,MIN] *= np.inf
inters_array[:,:,MAX] *= -np.inf

inters_details = np.ones(shape=(len(quads), len(coast_strs), len(energy_list), len(intensity_list)))

# Plot Quad heat loads
fig_ctr = 0

# special figure for coasting of 0.5
for quad_ctr, quad in enumerate(quads):
    if quad_ctr % 4 == 0:
        fig=plt.figure()
        fig_ctr += 1
        title_str = 'Heat loads for quadrupoles using a 0.5$\cdot 10^9$ coasting beam'
        plt.suptitle(title_str, fontsize=25)
        fig.canvas.set_window_title(title_str)
    sp = plt.subplot(2,2,quad_ctr%4+1)
    sp.set_xlabel('SEY Parameter')
    sp.set_ylabel('Heat load per m [W]')
    sp.set_title(quad)

    for key_ctr, key in enumerate(dict_keys):

        coast_ctr = 1
        coast_str = '0.5'
        data = pyecloud_device_easy('ArcQuadReal',coast_str)


        label = scenarios_labels_dict[key]

        if '450' in label:
            ls = ':'
        elif '6.5' in label:
            ls = '-'
        else:
            raise ValueError()

        if '0.9e11' in label:
            color = 'red'
        elif '1.1e11' in label:
            color = 'green'
        elif '0.7e11' in label:
            color = 'blue'
        else:
            raise ValueError()
        sp.plot(sey_list, data[key_ctr,:], label=label, color=color, ls=ls)

        measured = hl_pm_measured_quads[key_ctr,quad_ctr]
        sp.plot(sey_list, measured*one_list, ls=ls, color=color)

        # get intersection point
        sey_int = np.interp(measured,data[key_ctr,:],sey_list)
        inters_array[quad_ctr,coast_ctr,MIN] = min(inters_array[quad_ctr,coast_ctr,MIN], sey_int)
        inters_array[quad_ctr,coast_ctr,MAX] = max(inters_array[quad_ctr,coast_ctr,MAX], sey_int)

        energy_ctr, intensity_ctr = get_energy_intensity_ctr(key)
        inters_details[quad_ctr,coast_ctr,energy_ctr,intensity_ctr] = sey_int

    # Make nicer plots
    y_lim = sp.get_ylim()
    x_lim = sp.get_xlim()
    plot_min = max(x_lim[0]+0.005, min(inters_array[quad_ctr,:,MIN]))
    plot_max = min(x_lim[1]-0.005, max(inters_array[quad_ctr,:,MAX]))

    # Minimum/Maximum SEY for better overview
    plt.axvline(plot_min, y_lim[0], y_lim[1], ls='-', color='0.3', label='min/max SEY')
    plt.axvline(plot_max, y_lim[0], y_lim[1], ls='-', color='0.3')

    if quad_ctr % 4 == 1 or quad_ctr % 4 == 3:
        sp.legend(bbox_to_anchor=(1.1, 1))


# All coast_strs
for quad_ctr, quad in enumerate(quads):
    if quad_ctr % 4 == 0:
        fig=plt.figure()
        fig_ctr += 1
        title_str = 'Heat loads for quadrupoles' + ' %i' % fig_ctr
        plt.suptitle(title_str, fontsize=25)
        fig.canvas.set_window_title(title_str)
    sp = plt.subplot(2,2,quad_ctr%4+1)
    sp.set_xlabel('SEY Parameter')
    sp.set_ylabel('Heat load per m [W]')
    sp.set_title(quad)

    colors = itertools.cycle(plt.rcParams['axes.prop_cycle'])

    for key_ctr, key in enumerate(dict_keys):
        color = colors.next()[u'color']
        measured = hl_pm_measured_quads[key_ctr,quad_ctr]
        sp.plot(sey_list, measured*one_list, '--', color=color)

        for coast_ctr, coast_str in enumerate(coast_strs):
            data = pyecloud_device_easy('ArcQuadReal',coast_str)

            # get intersection point
            sey_int = np.interp(measured,data[key_ctr,:],sey_list)
            inters_array[quad_ctr,coast_ctr,MIN] = min(inters_array[quad_ctr,coast_ctr,MIN], sey_int)
            inters_array[quad_ctr,coast_ctr,MAX] = max(inters_array[quad_ctr,coast_ctr,MAX], sey_int)

            if coast_ctr == 0:
                label = scenarios_labels_dict[key]
            else:
                label = None
            ls = coast_linestyle_dict[coast_str]
            sp.plot(sey_list, data[key_ctr,:], label=label, color=color, ls=ls)

    # Make nicer plots
    y_lim = sp.get_ylim()
    x_lim = sp.get_xlim()
    plot_min = max(x_lim[0]+0.005, min(inters_array[quad_ctr,:,MIN]))
    plot_max = min(x_lim[1]-0.005, max(inters_array[quad_ctr,:,MAX]))

    # Minimum/Maximum SEY for better overview
    plt.axvline(plot_min, y_lim[0], y_lim[1], ls='-', color='0.3', label='min/max SEY')
    plt.axvline(plot_max, y_lim[0], y_lim[1], ls='-', color='0.3')

    if quad_ctr % 4 == 1:
        sp.legend(bbox_to_anchor=(1.1, 1))

# Plot Min/Max Intersections
# For all coasting beams

yylim_min = np.min(inters_details) - 0.05
yylim_max = np.max(inters_details) + 0.05

fig=plt.figure()
title_str = 'Min/Max SEY for Quadrupoles'
plt.suptitle(title_str,fontsize=25)
fig.canvas.set_window_title(title_str)

sp = plt.subplot(2,2,1)
sp.set_xlabel('Quadrupole Nr')
sp.set_ylabel('SEY Parameter')
sp.set_title('All coasting beams')

for quad_ctr, quad in enumerate(quads):
    min_inters = min(inters_array[quad_ctr,:,MIN])
    max_inters = max(inters_array[quad_ctr,:,MAX])
    plt.plot([quad_ctr+1]*2, [min_inters, max_inters], ls='-', label=quad)
sp.set_xlim(0,9)
sp.set_ylim(yylim_min, yylim_max)

# For each coasting beam individually
for coast_ctr, coast_str in enumerate(coast_strs):
    sp = plt.subplot(2,2,2+coast_ctr)
    sp.set_xlabel('Quadrupole Nr')
    sp.set_ylabel('SEY Parameter')
    sp.set_title('Coasting ' + coast_str + ' e9')

    for quad_ctr, quad in enumerate(quads):
        min_inters = inters_array[quad_ctr,coast_ctr,MIN]
        max_inters = inters_array[quad_ctr,coast_ctr,MAX]
        plt.plot([quad_ctr+1]*2, [min_inters, max_inters], ls='-', label=quad)
    sp.set_xlim(0,9)
    sp.set_ylim(yylim_min, yylim_max)

    if coast_ctr == 0:
        sp.legend(bbox_to_anchor=(1.1, 1))


# Intersection vs Intensity and Energy

xx = [1,2]
for quad_ctr, quad in enumerate(quads):
    sp_ctr  = quad_ctr % 4 + 1

    if sp_ctr == 1:
        fig = plt.figure()
        title = 'Inferred Quadrupole SEY depending on Energy and Intensity %i' % int((quad_ctr/4)+1)
        plt.suptitle(title, fontsize=25)
        fig.canvas.set_window_title(title)

    sp = plt.subplot(2,2,sp_ctr)
    sp.set_xlabel('Energy')
    sp.set_ylabel('Inferred SEY')
    sp.set_xticklabels(energy_list)
    sp.set_xticks(xx)
    sp.set_title(quad)
    sp.set_xlim(0.8,2.2)
    sp.set_ylim(yylim_min, yylim_max)

    for intensity_ctr, intensity in enumerate(intensity_list):
        yy = inters_details[quad_ctr,1,:,intensity_ctr]
        sp.plot(xx, yy, label=intensity, marker='x')

    if sp_ctr == 2:
        plt.legend(bbox_to_anchor=(1.1,1))

