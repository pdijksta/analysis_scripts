import numpy as np
import matplotlib.pyplot as plt
import itertools

from LHCMeasurementTools.mystyle import colorprog
from pyecloud_device import pyecloud_device
from simulation_parameters import *

intensity_ls_dict = {\
        '0.7e11': '-.',
        '0.9e11': '--',
        '1.1e11': '-'
        }

energy_ls_dict = {\
        '450GeV': '--',
        '6.5TeV': '-'
        }

one_list = np.ones_like(sey_list)
pyecloud_device_easy = lambda device, coast_str: pyecloud_device(device, coast_str, devices, coast_strs, hl_pyecloud)

title_str = 'Heat loads for different devices and scenarios, per m and scaled'

## All coasting strs
fig = plt.figure()
fig.canvas.set_window_title(title_str)
plt.suptitle(title_str,fontsize=25)

for dev_ctr, device in enumerate(devices):
    sp = plt.subplot(2,2,dev_ctr+1)
    title = device_labels_dict[device]
    sp.set_title(title)

    sp.set_xlabel('SEY Parameter')
    sp.set_ylabel('Heat load per m [W]')
    sp2 = sp.twinx()
    sp2.set_ylabel('Heat load per half cell [W]')
    sp2.grid('off')

    colors = itertools.cycle(plt.rcParams['axes.prop_cycle'])
    for sce_ctr, sce in enumerate(dict_keys):
        color = colors.next()['color']
        for coast_ctr, coast_str in enumerate(coast_strs):
            data = pyecloud_device_easy(device,coast_str)
            if coast_ctr == 0 and dev_ctr ==1:
                label = scenarios_labels_dict[sce]
            elif dev_ctr == 2 and sce_ctr == 0 :
                label = coast_str + ' e9 coasting'
            else:
                label = None
            ls = coast_linestyle_dict[coast_str]

            sp.plot(sey_list,data[sce_ctr,:],label=label,color=color, ls=ls)

    if dev_ctr == 1 or dev_ctr == 2:
        sp.legend(bbox_to_anchor=(1.1, 1),loc='upper left')

    axes_factor = length[device]
    unscaled_min, unscaled_max =  sp.get_ylim()
    sp2.set_ylim(axes_factor*unscaled_min,axes_factor*unscaled_max)

# For each coasting str
for coast_ctr, coast_str in enumerate(coast_strs):
    fig = plt.figure()
    title_str = 'Heat loads assuming a coasting beam of %s e9' % coast_str
    fig.canvas.set_window_title(title_str)
    plt.suptitle(title_str,fontsize=25)

    for dev_ctr, device in enumerate(devices):
        sp = plt.subplot(2,2,dev_ctr+1)
        title = device_labels_dict[device]
        sp.set_title(title)

        sp.set_xlabel('SEY Parameter')
        sp.set_ylabel('Heat load per m [W]')
        sp2 = sp.twinx()
        sp2.set_ylabel('Heat load per half cell [W]')
        sp2.grid('off')

        colors = list(plt.rcParams['axes.prop_cycle'])
        for sce_ctr, sce in enumerate(dict_keys):
            data = pyecloud_device_easy(device, coast_str)
            intensity = get_intensity(sce)
            intensity_ctr = intensity_list.index(intensity)

            energy = get_energy(sce)
            energy_ctr = energy_list.index(energy)
            color = colors[intensity_ctr][u'color']

            ls = energy_ls_dict[energy]
            if dev_ctr == 1 and ls == '-' :
                label = intensity
            elif dev_ctr == 2 and intensity_ctr == 2:
                label = energy
            else:
                label = None

            sp.plot(sey_list,data[sce_ctr,:], label=label, color=color, ls=ls)

        if dev_ctr == 1 or dev_ctr == 2:
            sp.legend(bbox_to_anchor=(1.1, 1), loc='upper left')

        axes_factor = length[device]
        unscaled_min, unscaled_max =  sp.get_ylim()
        sp2.set_ylim(axes_factor*unscaled_min, axes_factor*unscaled_max)

## Heat load vs Intensity
data = np.zeros(shape=(len(devices),len(energy_list), len(coast_strs), len(sey_list), len(intensity_list_float)))
for key_ctr, key in enumerate(dict_keys):
    energy = get_energy(key)
    energy_ctr = energy_list.index(energy)
    intensity = get_intensity(key)
    intensity_ctr = intensity_list.index(intensity)
    for dev_ctr, device in enumerate(devices):
        for coast_ctr, coast_str in enumerate(coast_strs):
            for sey_ctr, sey in enumerate(sey_list):
                data[dev_ctr,energy_ctr,coast_ctr,sey_ctr,intensity_ctr] = hl_pyecloud[key_ctr,dev_ctr,coast_ctr,sey_ctr]

for coast_ctr, coast_str in enumerate(coast_strs):
    for energy_ctr, energy in enumerate(energy_list):
        fig = plt.figure()
        title_str = 'Simulated heat loads for energy %s and coasting beam %s e9' % (energy, coast_str)
        fig.canvas.set_window_title(title_str)
        plt.suptitle(title_str,fontsize=25)

        for dev_ctr, device in enumerate(devices):
            sp = plt.subplot(2,2,dev_ctr+1)
            title = device_labels_dict[device]
            sp.set_title(title)

            sp.set_xlabel('Intensity')
            sp.set_ylabel('Heat load per m [W]')
            sp2 = sp.twinx()
            sp2.set_ylabel('Heat load per half cell [W]')
            sp2.grid('off')

            for sey_ctr, sey in enumerate(sey_list):
                if dev_ctr == 1:
                    label = sey
                else:
                    label = None
                color = colorprog(sey_ctr, len(sey_list))
                sp.plot(intensity_list_float,data[dev_ctr,energy_ctr,coast_ctr,sey_ctr,:], label=label, color=color)

            if dev_ctr == 1:
                sp.legend(bbox_to_anchor=(1.1, 1), loc='upper left')

            axes_factor = length[device]
            unscaled_min, unscaled_max =  sp.get_ylim()
            sp2.set_ylim(axes_factor*unscaled_min, axes_factor*unscaled_max)

