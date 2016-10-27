# Plot the electrons in the chamber for various devices, SEYs and coasting beams

import cPickle

import numpy as np
import matplotlib.pyplot as plt

from LHCMeasurementTools.mystyle import colorprog
from simulation_parameters import \
        dict_keys, scenarios_labels_dict, coast_linestyle_dict, coast_strs, sey_list, devices, device_labels_dict,\
        get_energy, get_intensity, get_filln, intensity_list_float, energy_list, intensity_list
from RcParams import init_pyplot
init_pyplot()


# Config
nel_hist_pkl_name = './all_data/nel_hist_pyecloud.pkl'
beam = 'B2'

# Load Pickle
with open(nel_hist_pkl_name, 'r') as pkl_file:
    nel_hist_dict = cPickle.load(pkl_file)

# data for x-Axis
xg_hist = nel_hist_dict['xg_hist']
xg_hist_cm = xg_hist * 100

# Plots
this_sey_list = ['1.10', '1.40', '1.50']
yy_zero = np.zeros_like(xg_hist)

for main_key in dict_keys:
    title_str = 'Electrons in the chamber %s %s' % (scenarios_labels_dict[main_key], beam)

    fig = plt.figure()
    fig.canvas.set_window_title(title_str)
    plt.suptitle(title_str,fontsize=25)

    for dev_ctr, device in enumerate(devices):
        sp = plt.subplot(2,2,dev_ctr+1)
        sp.set_xlabel('Chamber bin position [cm]')
        sp.set_ylabel('Number of $e^-$ per bin')
        sp.set_title(device_labels_dict[device])

        for coast_ctr, coast_str in enumerate(coast_strs):
            for sey_ctr, sey_str in enumerate(this_sey_list):
                if dev_ctr == 1 and sey_ctr == 0:
                    label = coast_str + ' e9 coasting'
                elif dev_ctr == 2 and coast_ctr == 0:
                    label = 'SEY %s' % sey_str
                else:
                    label = None
                ls = coast_linestyle_dict[coast_str]
                color = colorprog(sey_ctr, len(this_sey_list))

                try:
                    nel_hist = nel_hist_dict[main_key][device][coast_str][sey_str][beam]
                except KeyError:
                    #print(main_key,device,coast_str,sey_str,beam)
                    nel_hist = yy_zero
                sp.plot(xg_hist_cm,nel_hist,label=label,ls=ls,color=color)

        if dev_ctr == 1 or dev_ctr == 2:
            sp.legend(bbox_to_anchor=(1.1, 1))


def get_key(energy_ctr, intensity_ctr):
    for key_ctr, key in enumerate(dict_keys):
        if energy_list.index(get_energy(key)) == energy_ctr and \
                intensity_list.index(get_intensity(key)) == intensity_ctr:
            return key
    else:
        raise ValueError('No key for %i %i found' % (energy_ctr, intensity_ctr))


coast_str = '0.5'
coast_ctr = coast_strs.index(coast_str)

sey_dict = {\
        'ArcDipReal': [1.40, 1.45],
        'ArcQuadReal': [1.3, 1.4],
        'Drift': [1.3, 1.4]
        }

for energy_ctr, energy in enumerate(energy_list):
    fig = plt.figure()
    title = 'Comparison of Intensities for energy %s and coasting beam %s$\cdot 10^9$ %s' % (energy, coast_str, beam)
    fig.canvas.set_window_title(title)
    fig.suptitle(title, fontsize=25)

    for dev_ctr, device in enumerate(devices):
        sp = plt.subplot(2,2,dev_ctr+1)
        sp.set_xlabel('Chamber bin position [cm]')
        sp.set_ylabel('Number of $e^-$ per bin')
        sp.set_title(device_labels_dict[device] + ' ' + '%.2f SEY' % sey_dict[device][0])
        for intensity_ctr, intensity in enumerate(intensity_list):
            key = get_key(energy_ctr, intensity_ctr)
            dev_sey_list = sey_dict[device]
            for sey_ctr, sey in enumerate(dev_sey_list[:1]):
                sey_str = '%.2f' % sey
                try:
                    nel_hist = nel_hist_dict[key][device][coast_str][sey_str][beam]
                except KeyError:
                    print('Key Error for %s.' % device)
                    nel_hist = np.zeros_like(xg_hist)

                if dev_ctr == 1 and sey_ctr == 0:
                    label = '%s$\cdot 10^{11}$' % intensity
                else:
                    label = None
                sp.plot(xg_hist_cm, nel_hist,label=label)

        if dev_ctr == 1:
            plt.legend(bbox_to_anchor=(1.1, 1))

plt.show()
