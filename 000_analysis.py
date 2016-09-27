# Written by Philipp Dijkstal, philipp.dijkstal@cern.ch

import sys
import cPickle
import argparse
import re

import matplotlib.pyplot as plt
import numpy as np
import math 
import scipy.optimize as opt
from scipy.optimize.nonlin import NoConvergence


# Arguments

arg = argparse.ArgumentParser(description='')
arg.add_argument('-g', help='Show global optimization, do not use this flag!', action='store_true')
arg.add_argument('-d', help='Show heat loads for every device', action='store_true')
arg.add_argument('-a', help='Show heat loads on arcs fill by fill, do not use this flag!', action='store_true')
arg.add_argument('-q', help='Show heat loads on quads fill by fill', action='store_true')
arg.add_argument('-o', help='Dual Optimization', action='store_true')
args = arg.parse_args()


# Config

# The following two lists have to be in the right order
dict_keys = ['5219 1.8', '5219 0.92', '5222 2.3', '5223 3.0']
scenarios_labels = ['1.1e11 6.5TeV', '1.1e11 450GeV', '0.9e11 6.5TeV', '0.7e11 6.5TeV']

re_arc = re.compile('^S\d\d$')
re_quad = re.compile('^Q06[LR][1258]$')
re_quad_15 = re.compile('^Q06[LR][15]$')
re_quad_28 = re.compile('^Q06[LR][28]$')

model_key = 'Imp+SR'
imp_key = 'Imp'
#sr_key = 'SR' # not needed
device_list = ['ArcDipReal', 'ArcQuadReal', 'Drift']
device_labels = ['Dipole', 'Quadrupole', 'Drift']
coast_strs = ['1.0', '0.5']
sey_list = np.arange(1.1,1.51,0.05)

len_dip = 14.3
len_quad = 3.1
dip_per_halfcell = 3.
len_cell = 53.45
len_q6_28 = 8.567
len_q6_15 = 4.8

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
hl_measured_quads = np.empty(shape=(len(dict_keys),len(quads)))
arc_uncertainty = np.empty_like(hl_measured)
quad_uncertainty = np.empty_like(hl_measured_quads)

for key_ctr in xrange(len(dict_keys)):
    main_key = dict_keys[key_ctr]
    for arc_ctr in xrange(len(arcs)):
        arc = arcs[arc_ctr]
        hl_measured[key_ctr,arc_ctr] = heatloads_dict[main_key][arc][0] - heatloads_dict[main_key][arc][2]
        arc_uncertainty[key_ctr,arc_ctr] = heatloads_dict[main_key][arc][1]
    hl_measured[key_ctr,:] -= heatloads_dict[main_key][model_key][0]

    for quad_ctr in xrange(len(quads)):
        quad = quads[quad_ctr]
        # Correct for length
        if re_quad_15.match(quad):
            length_quad = len_q6_15
        elif re_quad_28.match(quad):
            length_quad = len_q6_28
        else:
            raise ValueError('Illegal Quad %s') % quad

        # heat loads per m are needed here
        hl_measured_quads[key_ctr,quad_ctr] = heatloads_dict[main_key][quad][0] / length_quad
        quad_uncertainty[key_ctr,quad_ctr] = heatloads_dict[main_key][quad][1] / length_quad

    hl_measured_quads[key_ctr,:] -= heatloads_dict[main_key][imp_key][0] / len_cell


# Simulation data

# Functions for global
def pyecloud_global(coast_str):
    if coast_str not in coast_strs:
        print('Wrong coasting beam in pyecloud_global')
        sys.exit()

    hl_pyecloud = np.zeros(shape=(len(dict_keys),len(sey_list)))

    for key_ctr in xrange(len(dict_keys)):
        for sey_ctr in xrange(len(sey_list)):
            main_key = dict_keys[key_ctr]
            sey_str = '%.2f' % sey_list[sey_ctr]
            for device in device_list:
                hl = 0
                try:
                    hl = heatloads_dict_pyecloud[main_key][device][coast_str][sey_str][0]
                except KeyError:
                    print('Key error for fill %s, device %s sey %s coast %s.' % (main_key, device, sey_str, coast_str))
                    continue
                if heatloads_dict_pyecloud[main_key][device][coast_str][sey_str][1] == 1:
                    print('Correction for fill %s, device %s sey %s coast %s.' % (main_key, device, sey_str, coast_str))
                    hl *= 2

                hl_pyecloud[key_ctr,sey_ctr] += hl*length[device]

    return hl_pyecloud

def get_delta(hl_pyecloud):
    delta = np.zeros(shape=(len(arcs),len(sey_list),2))
    for arc_ctr in xrange(len(arcs)):
        for sey_ctr in xrange(len(sey_list)):
            delta[arc_ctr,sey_ctr,0] = sey_list[sey_ctr]

            for key_ctr in xrange(len(dict_keys)):
                measured = hl_measured[key_ctr,arc_ctr]
                pyecloud = hl_pyecloud[key_ctr,sey_ctr]
                delta[arc_ctr,sey_ctr,1] += ((measured-pyecloud)/measured)**2

            delta[arc_ctr,sey_ctr,1] = np.sqrt(delta[arc_ctr,sey_ctr,1])

    return delta

# Function for device
def pyecloud_device(device, coast_str):
    if device not in device_list or coast_str not in coast_str:
        print('Wrong device name in pyecloud_device!')
        sys.exit()

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

# Interpolate data for dual optim
def data_for_dual_optim():
    dip_begin = 1.15
    dip_end = 1.49
    step = 0.01
    dip_sey_list = np.arange(dip_begin,dip_end+.1*step,step)

    dip_data = (pyecloud_device('ArcDipReal','0.5') + pyecloud_device('ArcDipReal','1.0'))/2*length['ArcDipReal']
    quad_raw = pyecloud_quad()
    quad_data = np.mean(quad_raw,axis=2)*length['ArcQuadReal']

    output = np.zeros(shape=(len(dict_keys),len(arcs),len(dip_sey_list),2))
    for key_ctr in xrange(len(dict_keys)):
        for arc_ctr in xrange(len(arcs)):
            measured = hl_measured[key_ctr,arc_ctr]

            for dip_ctr, dip_sey in enumerate(dip_sey_list):
                dip_hl = np.interp(dip_sey,sey_list,dip_data[key_ctr,:])

                f_tobe_zero = lambda quad_sey: (measured - dip_hl - np.interp(quad_sey[0], sey_list, quad_data[key_ctr,:]))**2
                output[key_ctr,arc_ctr,dip_ctr,0] = dip_sey
                if dip_hl + quad_data[key_ctr,0] > measured or dip_hl + quad_data[key_ctr,-1] < measured:
                    #print('continue for %.2f' % dip_sey)
                    continue
                try:
                    output[key_ctr,arc_ctr,dip_ctr,1] = opt.newton_krylov(f_tobe_zero, [dip_sey-0.1], verbose=False)
                except (ValueError, NoConvergence):
                    #print('error', dip_sey)
                    pass
                else:
                    print(output[key_ctr,arc_ctr,dip_ctr,:])
    return output


# Plots
one_list = np.ones_like(sey_list)

# Dual optimization
if args.o:
    data = data_for_dual_optim()
    fig_ctr = 0
    for arc_ctr, arc in enumerate(arcs):
        if arc_ctr%4 == 0:
            fig = plt.figure()
            fig_ctr += 1
            title_str = 'Valid pairs of dip and quad SEY %i' % fig_ctr
            plt.suptitle(title_str,fontsize=22)
            fig.canvas.set_window_title(title_str)

        sp = plt.subplot(2,2,arc_ctr%4+1)

        # pyecloud data, measured only for labels/title
        for key_ctr, key in enumerate(dict_keys[:3]):
            hl = hl_measured[key_ctr,arc_ctr]
            label = '%s %.1f W' % (scenarios_labels[key_ctr],hl)
            possible_xdata = data[key_ctr,arc_ctr,:,0]
            possible_ydata = data[key_ctr,arc_ctr,:,1]
            xdata, ydata = [], []
            for ctr, yy in enumerate(possible_ydata):
                if yy != 0:
                    xdata.append(possible_xdata[ctr])
                    ydata.append(yy)

            plt.plot(xdata, ydata, label=label)

        # Add diagonal lines
        ylim = sp.get_ylim()
        xlim = sp.get_xlim()
        diag_left = max(ylim[0], xlim[0])
        diag_right = min(ylim[1],xlim[1])
        sp.plot([diag_left, diag_right], [diag_left,diag_right], '--', color='black', label='diagonal')

        sp.set_title('Arc %s' % arc, fontsize=20)
        sp.set_xlabel('Dipole SEY', fontsize=18)
        sp.set_ylabel('Quad SEY', fontsize=18)
        sp.legend(loc='upper right')

# Global optimization
if args.g:
    fig = plt.figure()
    title_str = 'Comparison of measured to pyecloud heat loads, %i scenarios' % len(dict_keys)
    fig.canvas.set_window_title(title_str)
    plt.suptitle(title_str, fontsize=16)

    coast_subplot = (plt.subplot(2,1,1), plt.subplot(2,1,2))

    for coast_ctr, coast_str in enumerate(coast_strs):
        delta = get_delta(pyecloud_global(coast_str))
        subplot = coast_subplot[coast_ctr]

        subplot.set_ylim(0,5)
        subplot.set_title('Coasting Beam of %s' % coast_str)
        subplot.set_xlabel('SEY Parameter')
        subplot.set_ylabel('RMS deviation')

        for arc_ctr, label in enumerate(arcs):
            subplot.plot(delta[arc_ctr,:,0], delta[arc_ctr,:,1], label=label)
            subplot.legend()

    plt.subplots_adjust(right=0.7, wspace=0.30)

# All devices
if args.d:
    fig = plt.figure()
    title_str = 'Heat loads for different devices and scenarios, per m and scaled'
    fig.canvas.set_window_title(title_str)
    plt.suptitle(title_str,fontsize=22)

    for dev_ctr, device in enumerate(device_list):
        sp = plt.subplot(len(device_list),1,dev_ctr+1)
        title = device_labels[dev_ctr]
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
            for sce_ctr in xrange(len(dict_keys)):
                label = scenarios_labels[sce_ctr] + ' ' + coast_str + 'e9 coasting'
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

    for key_ctr in xrange(len(dict_keys)):
        if key_ctr == 0:
            sp = plt.subplot(2,2,key_ctr+1)
        else:
            sp = plt.subplot(2,2,key_ctr+1,sharex=sp)
        sp.set_xlabel('SEY Parameter',fontsize=18)
        sp.set_ylabel('Heat load [W]',fontsize=18)

        uncertainty = np.mean(arc_uncertainty[key_ctr,:])
        uncertainty_str = 'Mean heat load uncertainty: %.1f W' % uncertainty
        sp.set_title(scenarios_labels[key_ctr]+'\n'+uncertainty_str, fontsize=20)

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

    for key_ctr in xrange(len(dict_keys)):
        if key_ctr == 0:
            sp = plt.subplot(2,2,key_ctr+1)
        else:
            sp = plt.subplot(2,2,key_ctr+1,sharex=sp)
        sp.set_xlabel('SEY Parameter', fontsize=18)
        sp.set_ylabel('Heat load per m [W]', fontsize=18)

        uncertainty = np.mean(quad_uncertainty[key_ctr,:])
        uncertainty_str = 'Mean heat load uncertainty: %.1f W' % uncertainty
        sp.set_title(scenarios_labels[key_ctr]+'\n'+uncertainty_str, fontsize=20)

        # measured data
        for quad_ctr in xrange(len(quads)):
            label = quads[quad_ctr]

            # Skip 15 quads as the data quality seems to be bad unfortunately
            if re_quad_15.match(label):
                continue
            sp.plot(sey_list, hl_measured_quads[key_ctr,quad_ctr]*one_list, '--', label=label)

        # simulation data
        for coast_ctr in xrange(len(coast_strs)):
            coast_str = coast_strs[coast_ctr]
            label = coast_str + 'e9 coasting'
            sp.plot(sey_list, data[key_ctr,:,coast_ctr], label=label)

        if key_ctr == 1:
            sp.legend(bbox_to_anchor=(1.1, 1),loc='upper left',fontsize=18)

plt.show()
