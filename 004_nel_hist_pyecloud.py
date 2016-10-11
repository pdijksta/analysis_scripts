import sys
import cPickle
import argparse

import numpy as np
import matplotlib.pyplot as plt

from LHCMeasurementTools.mystyle import colorprog
from simulation_parameters import \
        dict_keys, scenarios_labels_dict, coast_linestyle_dict, coast_strs, sey_list, devices, device_labels_dict,\
        get_energy, get_intensity, get_filln
from RcParams import init_pyplot
init_pyplot()

# Config
nel_hist_pkl_name = './nel_hist_pyecloud.pkl'

# Load Pickle
with open(nel_hist_pkl_name, 'r') as pkl_file:
    nel_hist_dict = cPickle.load(pkl_file)

# data for x-Axis
xg_hist = nel_hist_dict['xg_hist']


# Compare coasting beams
beam = 'B1'
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
                sp.plot(xg_hist*100,nel_hist,label=label,ls=ls,color=color)

        sp.legend(bbox_to_anchor=(1.1, 1))
plt.show()
