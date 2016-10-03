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

device_list = ['ArcDipReal', 'ArcQuadReal', 'Drift']
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


# Simulation data
# Sum over beam 1 and 2
hl_pyecloud = np.zeros(shape=(len(dict_keys),len(device_list),len(coast_strs),len(sey_list)))
for key_ctr, key in enumerate(dict_keys):
    for device_ctr, device in enumerate(device_list):
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

                hl_pyecloud[key_ctr,device_ctr,coast_ctr,sey_ctr] += hl*length[device]

# Function for device
def pyecloud_device(device, coast_str):
    if device not in device_list or coast_str not in coast_str:
        raise ValueError('Wrong device name or coast string in pyecloud_device!')

    hl_pyecloud = np.zeros(shape=(len(dict_keys),len(sey_list)))


    for key_ctr in xrange(len(dict_keys)):
        for sey_ctr in xrange(len(sey_list)):
            main_key = dict_keys[key_ctr]
            sey_str = '%.2f' % sey_list[sey_ctr]
            try:
                hl = heatloads_dict_pyecloud[main_key][device][coast_str][sey_str][0]
            except KeyError:
                print('Key error for fill %s, device %s sey %s coast %s.' % (main_key, device, sey_str, coast_str))
                continue
            if heatloads_dict_pyecloud[main_key][device][coast_str][sey_str][1] == 1:
                print('Correction for fill %s, device %s sey %s coast %s.' % (main_key, device, sey_str, coast_str))
                hl *= 2

            hl_pyecloud[key_ctr,sey_ctr] = hl

    return hl_pyecloud

# Function for quad only
def pyecloud_quad():
    hl_pyecloud = np.zeros(shape=(len(dict_keys),len(sey_list),len(coast_strs)))
    for coast_ctr, coast_str in enumerate(coast_strs):
        hl_pyecloud[:,:,coast_ctr] = pyecloud_device('ArcQuadReal',coast_str)

    return hl_pyecloud

# Plots
plt.close('all')
one_list = np.ones_like(sey_list)

# Dual optimization
if args.o:
    pass

 # Global optimization
if args.g:
    from d000_analysis.global_optimization import main
    main(dict_keys,arcs,sey_list,coast_strs,hl_measured,hl_pyecloud)


# All devices
if args.d:
    fig = plt.figure()
    title_str = 'Heat loads for different devices and scenarios, per m and scaled'
    fig.canvas.set_window_title(title_str)
    plt.suptitle(title_str,fontsize=22)

    for dev_ctr, device in enumerate(device_list):
        sp = plt.subplot(len(device_list),1,dev_ctr+1)
        title = device_labels_dict[device]
        sp.set_title(title,fontsize=20)
        if dev_ctr == len(device_list)-1:
            sp.set_xlabel('SEY Parameter',fontsize=18)
        sp.set_ylabel('Heat load per m [W]',fontsize=18)
        sp2 = sp.twinx()
        sp2.set_ylabel('Heat load per half cell [W]',fontsize=18)
        sp2.grid('off')
        if device == 'ArcDipReal':
            sp2.plot(sey_list,np.min(hl_measured)*one_list,label='Min measured')
            sp2.plot(sey_list,np.max(hl_measured)*one_list,label='Max measured')
            sp2.legend(bbox_to_anchor=(1.1, 1),loc='upper left',fontsize=18)

        for coast_ctr, coast_str in enumerate(coast_strs):
            data = pyecloud_device(device,coast_str)
            for sce_ctr,sce in enumerate(dict_keys):
                label = scenarios_labels_dict[sce_ctr] + ' ' + coast_str + 'e9 coasting'
                sp.plot(sey_list,data[sce_ctr,:],label=label)

        if dev_ctr == 1:
            sp.legend(bbox_to_anchor=(1.1, 1),loc='upper left',fontsize=18)
        axes_factor = length[device]
        unscaled_min, unscaled_max =  sp.get_ylim()
        sp2.set_ylim(axes_factor*unscaled_min,axes_factor*unscaled_max)

    plt.subplots_adjust(right=0.75, wspace=0.25)

# Arcs
if args.a:
    fig = plt.figure()
    title_str = 'Half cell heat loads'
    fig.canvas.set_window_title(title_str)
    plt.suptitle(title_str,fontsize=24)
    plt.subplots_adjust(right=0.8, wspace=0.20)
    datas = {}
    datas['0.5'] = pyecloud_global('0.5')
    datas['1.0'] = pyecloud_global('1.0')

    sp = None
    for key_ctr,key in enumerate(dict_keys):
        sp = plt.subplot(2,2,key_ctr+1,sharex=sp)
        sp.set_xlabel('SEY Parameter',fontsize=18)
        sp.set_ylabel('Heat load [W]',fontsize=18)

        uncertainty = np.mean(arc_uncertainty[key_ctr,:])
        uncertainty_str = 'Mean heat load uncertainty: %.1f W' % uncertainty
        sp.set_title(scenarios_labels_dict[key]+'\n'+uncertainty_str, fontsize=20)

        for arc_ctr in xrange(len(arcs)):
            label = arcs[arc_ctr]
            sp.plot(sey_list, hl_measured[key_ctr,arc_ctr]*one_list, '--', label=label)

        for coast_ctr in xrange(len(coast_strs)):
            coast_str = coast_strs[coast_ctr]
            label = coast_str + 'e9 coasting beam'
            data = datas[coast_str]
            sp.plot(sey_list, data[key_ctr,:], label=label)

        if key_ctr == 1:
            sp.legend(bbox_to_anchor=(1.1, 1),loc='upper left',fontsize=18)

# Quadrupoles
if args.q:
    fig = plt.figure()
    title_str = 'Fill by Fill Q6IR5 heat loads - 8m Quadrupoles'
    fig.canvas.set_window_title(title_str)
    plt.suptitle(title_str,fontsize=20)
    plt.subplots_adjust(right=0.8, wspace=0.20)

    data = pyecloud_quad()

    for key_ctr,key in enumerate(dict_keys):
        if key_ctr == 0:
            sp = plt.subplot(2,2,key_ctr+1)
        else:
            sp = plt.subplot(2,2,key_ctr+1,sharex=sp)
        sp.set_xlabel('SEY Parameter', fontsize=18)
        sp.set_ylabel('Heat load per m [W]', fontsize=18)

        uncertainty = np.mean(quad_uncertainty[key_ctr,:])
        uncertainty_str = 'Mean heat load uncertainty: %.1f W' % uncertainty
        sp.set_title(scenarios_labels_dict[key]+'\n'+uncertainty_str, fontsize=20)

        # measured data
        for quad_ctr, label in enumerate(quads):
            # Skip 15 quads as the data quality seems to be bad unfortunately
            if re_quad_15.match(label):
                continue
            sp.plot(sey_list, hl_pm_measured_quads[key_ctr,quad_ctr]*one_list, '--', label=label)

        # simulation data
        for coast_ctr, coast_str in enumerate(coast_strs):
            label = coast_str + 'e9 coasting'
            sp.plot(sey_list, data[key_ctr,:,coast_ctr], label=label)

        if key_ctr == 1:
            sp.legend(bbox_to_anchor=(1.1, 1),loc='upper left',fontsize=18)

plt.show()
