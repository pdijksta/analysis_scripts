# Written by Philipp Dijkstal, philipp.dijkstal@cern.ch

import sys
import cPickle
import argparse
import re

import matplotlib.pyplot as plt
import numpy as np
import math 

from LHCMeasurementTools.LHC_Heatloads import magnet_length

# Arguments

arg = argparse.ArgumentParser(description='')
arg.add_argument('-g', help='Show global optimization, do not use this flag!', action='store_true')
arg.add_argument('-d', help='Show heat loads for every device', action='store_true')
arg.add_argument('-a', help='Show heat loads on arcs fill by fill, do not use this flag!', action='store_true')
arg.add_argument('-q', help='Show heat loads on quads fill by fill', action='store_true')
arg.add_argument('-o', help='Dual Optimization', action='store_true')
args = arg.parse_args()


# Config

# Parameters of the analyzed study
dict_keys = ['5219 1.8', '5219 0.92', '5222 2.3', '5223 3.0']
scenarios_labels_dict = {'5219 1.8': '1.1e11 6.5TeV', 
        '5219 0.92': '1.1e11 450GeV', 
        '5222 2.3': '0.9e11 6.5TeV',
        '5223 3.0': '0.7e11 6.5TeV'}

coast_strs = ['1.0', '0.5']

sey_list = np.arange(1.1,1.51,0.05)

devices = ['ArcDipReal', 'ArcQuadReal', 'Drift']
device_labels_dict = {'ArcDipReal': 'Dipole', 
        'ArcQuadReal': 'Quadrupole',
        'Drift': 'Drift'}

# Names of devices
re_arc = re.compile('^S\d\d$')
re_quad = re.compile('^Q06[LR][1258]$')
re_quad_15 = re.compile('^Q06[LR][15]$')
re_quad_28 = re.compile('^Q06[LR][28]$')

model_key = 'Imp+SR'
imp_key = 'Imp'
#sr_key = 'SR' # not needed

len_dip = magnet_length['special_HC_D2'][0]
len_quad = magnet_length['special_HC_Q1'][0]
dip_per_halfcell = 3.
len_cell = magnet_length['AVG_ARC'][0]
len_q6_28 = magnet_length['Q6s_IR2'][0]
len_q6_15 = magnet_length['Q6s_IR1'][0]

length = {}
length['ArcQuadReal'] = len_quad
length['ArcDipReal'] = dip_per_halfcell * len_dip
length['Drift'] = len_cell - length['ArcDipReal'] - length['ArcQuadReal']
length['HalfCell'] = len_cell

ticksize = 14
plt.rcParams['axes.grid'] = True
plt.rcParams['legend.loc'] = 'upper left'
plt.rcParams['ytick.labelsize'] = ticksize
plt.rcParams['xtick.labelsize'] = ticksize


# Import nested dictionaries

with open('./heatload_arcs.pkl', 'r') as pickle_file:
    heatloads_dict = cPickle.load(pickle_file)

arc_quad_model_keys = heatloads_dict[dict_keys[0]].keys()

arcs = []
quads = []
for key in arc_quad_model_keys:
    if re_arc.match(key):
        arcs.append(key)
    elif re_quad.match(key):
        quads.append(key)

with open('./heatload_pyecloud.pkl', 'r') as pickle_file:
    heatloads_dict_pyecloud = cPickle.load(pickle_file)


# Measured data
hl_measured = np.empty(shape=(len(dict_keys),len(arcs)))
hl_pm_measured_quads = np.empty(shape=(len(dict_keys),len(quads)))
arc_uncertainty = np.empty_like(hl_measured)
quad_uncertainty = np.empty_like(hl_pm_measured_quads)

for key_ctr, key in enumerate(dict_keys):
    for arc_ctr,arc in enumerate(arcs):
        hl_measured[key_ctr,arc_ctr] = heatloads_dict[key][arc][0] - heatloads_dict[key][arc][2]
        arc_uncertainty[key_ctr,arc_ctr] = heatloads_dict[key][arc][1]
    hl_measured[key_ctr,:] -= heatloads_dict[key][model_key][0]

    for quad_ctr,quad in enumerate(quads):
        # Correct for length
        if re_quad_15.match(quad):
            length_quad = len_q6_15
        elif re_quad_28.match(quad):
            length_quad = len_q6_28
        else:
            raise ValueError('Illegal Quad %s') % quad

        # heat loads per m are needed here
        hl_pm_measured_quads[key_ctr,quad_ctr] = heatloads_dict[key][quad][0] / length_quad
        quad_uncertainty[key_ctr,quad_ctr] = heatloads_dict[key][quad][1] / length_quad

    hl_pm_measured_quads[key_ctr,:] -= heatloads_dict[key][imp_key][0] / len_cell
# Heat load per m
hl_pm_measured = hl_measured / len_cell


# Simulation data
# Sum over beam 1 and 2
hl_pyecloud = np.zeros(shape=(len(dict_keys),len(devices),len(coast_strs),len(sey_list)))
for key_ctr, key in enumerate(dict_keys):
    for device_ctr, device in enumerate(devices):
        for coast_ctr, coast_str in enumerate(coast_strs):
            for sey_ctr, sey in enumerate(sey_list):
                sey_str = '%.2f' % sey
                hl = 0
                try:
                    hl = heatloads_dict_pyecloud[key][device][coast_str][sey_str][0]
                except KeyError:
                    print('Key error for fill %s, device %s sey %s coast %s.' % (main_key, device, sey_str, coast_str))
                    continue
                # If no sim data for one beam, double the heatload from the other beam
                if heatloads_dict_pyecloud[key][device][coast_str][sey_str][1] == 1:
                    print('Correction for fill %s, device %s sey %s coast %s.' % (key, device, sey_str, coast_str))
                    hl *= 2

                hl_pyecloud[key_ctr,device_ctr,coast_ctr,sey_ctr] += hl

# Plots
plt.close('all')
one_list = np.ones_like(sey_list)

# Dual optimization
if args.o:
    from d000_analysis.dual_optimization import main
    main(hl_pyecloud, devices, coast_strs, scenarios_labels_dict, length, dict_keys, arcs, hl_measured, sey_list)

 # Global optimization
if args.g:
    from d000_analysis.global_optimization import main
    main(dict_keys,arcs,sey_list,coast_strs,hl_pm_measured,hl_pyecloud)

# All devices
if args.d:
    from d000_analysis.devices import main
    main(devices,device_labels_dict, sey_list, coast_strs, dict_keys, hl_pm_measured, hl_pyecloud, scenarios_labels_dict, length)

# Arcs
if args.a:
    from d000_analysis.arcs import main
    main(hl_pyecloud, hl_measured, length, arc_uncertainty, scenarios_labels_dict, arcs, sey_list, coast_strs, dict_keys, devices)
    
# Quadrupoles
if args.q:
    from d000_analysis.quads import main
    main(devices, coast_strs, hl_pyecloud, hl_pm_measured_quads, dict_keys, quad_uncertainty, quads, sey_list, scenarios_labels_dict)
    
plt.show()
