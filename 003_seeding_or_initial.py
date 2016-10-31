import sys
import cPickle

import numpy as np
import matplotlib.pyplot as plt

import LHCMeasurementTools.mystyle as ms
from LHCMeasurementTools.LHC_Heatloads import magnet_length
len_cell = magnet_length['AVG_ARC'][0]
from simulation_parameters import sey_list, coast_strs, device_labels_dict, scenarios_labels_dict
from RcParams import init_pyplot
init_pyplot()

seeding_pkl_file = './seeding/data_seeding_3/heatload_pyecloud.pkl'
initial_pkl_file = './all_data/heatload_pyecloud.pkl'

with open(seeding_pkl_file, 'r') as f:
    hl_pyecloud_seeding_dict = cPickle.load(f)
with open(initial_pkl_file, 'r') as f:
    hl_pyecloud_initial_dict = cPickle.load(f)

dict_keys_seeding= hl_pyecloud_seeding_dict.keys()
devices_seeding = ['ArcDipReal', 'ArcQuadReal']
hl_seeding = np.zeros(shape=(len(dict_keys_seeding),len(devices_seeding),len(coast_strs),len(sey_list)))
hl_initial = np.zeros_like(hl_seeding)

for key_ctr, key in enumerate(dict_keys_seeding):
    for device_ctr, device in enumerate(devices_seeding):
        for coast_ctr, coast_str in enumerate(coast_strs):
            for sey_ctr, sey in enumerate(sey_list):
                sey_str = '%.2f' % sey
                try:
                    hl = hl_pyecloud_seeding_dict[key][device][coast_str][sey_str]['Total']
                except KeyError:
                    print('Key error for fill %s, device %s sey %s coast %s.' % (key, device, sey_str, coast_str))
                else:
                    # If no sim data for one beam, double the heatload from the other beam
                    if hl_pyecloud_seeding_dict[key][device][coast_str][sey_str]['Beam_nr'] == 1:
                        print('Correction for fill %s, device %s sey %s coast %s.' % (key, device, sey_str, coast_str))
                        hl *= 2

                    hl_seeding[key_ctr,device_ctr,coast_ctr,sey_ctr] += hl

                try:
                    hl = hl_pyecloud_initial_dict[key][device][coast_str][sey_str]['Total']
                except KeyError:
                    print('Key error for fill %s, device %s sey %s coast %s.' % (key, device, sey_str, coast_str))
                else:
                    # If no sim data for one beam, double the heatload from the other beam
                    if hl_pyecloud_initial_dict[key][device][coast_str][sey_str]['Beam_nr'] == 1:
                        print('Correction for fill %s, device %s sey %s coast %s.' % (key, device, sey_str, coast_str))
                        hl *= 2

                    hl_initial[key_ctr,device_ctr,coast_ctr,sey_ctr] += hl


for device_ctr, device in enumerate(devices_seeding):
    fig = plt.figure()
    title = 'Comparison between seeding mechanisms %s' % device_labels_dict[device]
    fig.canvas.set_window_title(title)
    plt.suptitle(title, fontsize=25)

    for coast_ctr, coast_str in enumerate(coast_strs):
        sp_ctr = coast_ctr+1
        sp = plt.subplot(2,2,sp_ctr)
        sp.set_xlabel('SEY Parameter')
        sp.set_ylabel('Heat load [W/m]')
        sp.set_title('%s$\cdot 10^9$ coasting' % coast_str)
        sp2 = sp.twinx()
        sp2.grid('off')

        for key_ctr, key in enumerate(dict_keys_seeding):

            if sp_ctr == 2:
                label1 = scenarios_labels_dict[key]
                label2=None
            elif sp_ctr == 3 and key_ctr == 0:
                label1 = 'Photoemission'
                label2 = 'Initial e-cloud'
            else:
                label1 = label2 = None

            color = ms.colorprog(key_ctr, len(dict_keys_seeding))

            sp.plot(sey_list, hl_seeding[key_ctr, device_ctr, coast_ctr,:], color=color, ls='-', label=label1)
            sp.plot(sey_list, hl_initial[key_ctr, device_ctr, coast_ctr,:], color=color, ls='--', label=label2)

        sp_lims = sp.get_ylim()
        sp2.set_ylim(sp_lims[0]*len_cell, sp_lims[1]*len_cell)
        if sp_ctr == 2 or sp_ctr == 3:
            sp.legend(bbox_to_anchor=(1.1,1))

plt.show()
