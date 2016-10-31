import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import itertools

sys.path.append('..')
from pyecloud_device import pyecloud_device
from simulation_parameters import *
from RcParams import init_pyplot
init_pyplot()

# DEFINE
MIN, MAX = 0, 1
assumed_sey = 1.2

one_list = np.ones_like(sey_list)
pyecloud_device_easy = lambda device, coast_str: pyecloud_device(device, coast_str, devices, coast_strs, hl_pyecloud)

# intersection points
inters_array = np.ones(shape=(len(arcs), len(coast_strs), 2))
inters_array[:,:,MIN] *= np.inf
inters_array[:,:,MAX] *= -np.inf

# Plot Quad heat loads
fig_ctr = 0

dict_keys_le = []
for key in dict_keys:
    if '450GeV' in scenarios_labels_dict[key]:
        dict_keys_le.append(key)

print(dict_keys_le)

sey_ctr = get_sey_ctr(1.2, sey_list)
quad_assumed_sey = pyecloud_device_easy('ArcQuadReal', '0.5')[:,sey_ctr]

for arc_ctr, arc in enumerate(arcs):
    if arc_ctr % 4 == 0:
        fig=plt.figure()
        fig_ctr += 1
        title_str = 'Heat loads for Arcs' + ' %i' % fig_ctr
        plt.suptitle(title_str, fontsize=25)
        fig.canvas.set_window_title(title_str)
    sp = plt.subplot(2,2,arc_ctr%4+1)
    sp.set_xlabel('SEY Parameter')
    sp.set_ylabel('Heat load [W/m]')
    sp.set_title(arc)

    colors = itertools.cycle(plt.rcParams['axes.prop_cycle'])

    for key_ctr, key in enumerate(dict_keys):
        if key not in dict_keys_le:
            continue
        color = colors.next()[u'color']
        measured = hl_measured[key_ctr,arc_ctr]
        sp.plot(sey_list, measured*one_list, '--', color=color)
        #sp.plot(sey_list,

        for coast_ctr, coast_str in enumerate(coast_strs):
            data = pyecloud_device_easy('ArcDipReal',coast_str)[key_ctr,:]*length['ArcDipReal'] + quad_assumed_sey[key_ctr]*length['ArcQuadReal']

            # get intersection point
            sey_int = np.interp(measured,data,sey_list)
            inters_array[arc_ctr,coast_ctr,MIN] = min(inters_array[arc_ctr,coast_ctr,MIN], sey_int)
            inters_array[arc_ctr,coast_ctr,MAX] = max(inters_array[arc_ctr,coast_ctr,MAX], sey_int)

            if coast_ctr == 1:
                label = scenarios_labels_dict[key]
            else:
                label = None
            ls = '-'

            # ugly hack
            if coast_ctr == 1:
                sp.plot(sey_list, data, label=label, color=color, ls=ls)

    # Make nicer plots
    y_lim = sp.get_ylim()
    x_lim = sp.get_xlim()
    plot_min = max(x_lim[0]+0.005, inters_array[arc_ctr,1,MIN])
    plot_max = min(x_lim[1]-0.005, inters_array[arc_ctr,1,MAX])

    # Minimum/Maximum SEY for better overview
    plt.axvline(plot_min, y_lim[0], y_lim[1], ls='-', color='0.3', label='min/max SEY')
    plt.axvline(plot_max, y_lim[0], y_lim[1], ls='-', color='0.3')

    if arc_ctr % 4 == 1:
        sp.legend(bbox_to_anchor=(1.1, 1))


# Plot Min/Max Intersections
# For all coasting beams
fig=plt.figure()
title_str = 'Min/Max SEY for dipoles, assuming a quad SEY of %.2f' % assumed_sey
plt.suptitle(title_str,fontsize=25)
fig.canvas.set_window_title(title_str)

sp = plt.subplot(2,2,1)
sp.set_xlabel('Arc Nr')
sp.set_ylabel('SEY Parameter')
sp.set_title('All coasting beams')

for arc_ctr, arc in enumerate(arcs):
    min_inters = min(inters_array[arc_ctr,:,MIN])
    max_inters = max(inters_array[arc_ctr,:,MAX])
    plt.plot([arc_ctr+1]*2, [min_inters, max_inters], ls='-', label=arc)
sp.set_xlim(0,9)

# For each coasting beam individually
for coast_ctr, coast_str in enumerate(coast_strs):
    sp = plt.subplot(2,2,2+coast_ctr)
    sp.set_xlabel('Arc')
    sp.set_ylabel('SEY Parameter')
    sp.set_title('Coasting ' + coast_str + ' e9')

    for arc_ctr, arc in enumerate(arcs):
        min_inters = inters_array[arc_ctr,coast_ctr,MIN]
        max_inters = inters_array[arc_ctr,coast_ctr,MAX]
        plt.plot([arc_ctr+1]*2, [min_inters, max_inters], ls='-', label=arc)
    sp.set_xlim(0,9)

    if coast_ctr == 0:
        sp.legend(bbox_to_anchor=(1.1, 1))


plt.show()
sys.exit()
