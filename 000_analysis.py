#!/usr/bin/python2

# Written by Philipp Dijkstal, philipp.dijkstal@cern.ch

import os
import sys
import cPickle
import argparse

import matplotlib.pyplot as plt
import numpy as np

arg = argparse.ArgumentParser(description='')
arg.add_argument('-g',help='Show global optimization',action='store_true')
arg.add_argument('-d',help='Show heatloads for every device',action='store_true')
arg.add_argument('-a',help='Show heatloads on arcs fill by fill',action='store_true')
arg.add_argument('-q',help='Show heatloads on quads fill by fill',action='store_true')

args = arg.parse_args()

# config
sey_list = np.arange(1.1,1.46,0.05)
coast_strs = ['1.0', '0.5']
dict_keys = [['5219','1.8'], ['5219','0.92'], ['5222','2.3'], ['5223','3.0']]
scenarios_labels = [ '1.1e11 6.5TeV', '1.1e11 450GeV', '0.9e11 6.5TeV', '0.7e11 6.5TeV']

arcs = ['S45', 'S23', 'S12', 'S81', 'S78', 'S56', 'S34', 'S67']
quads = ['Q05L1', 'Q05R1', 'Q05L5','Q05R5']
model = 'Imp+SR'
device_list = ['ArcDipReal', 'ArcQuadReal', 'Drift']
device_labels = ['Dipole' , 'Quadrupole', 'Drift']

len_dip = 14.3
len_quad = 3.1
dip_per_halfcell = 3
len_cell = 53.45
len_q6 = 8

ticksize = 14
#plt.rcParams['axes.labelsize'] = ticksize
plt.rcParams['axes.grid'] = True
plt.rcParams['legend.loc'] = 'upper left'
plt.rcParams['ytick.labelsize'] = ticksize
plt.rcParams['xtick.labelsize'] = ticksize


# import nested dictionaries
with open('./heatload_arcs.pkl','r') as pickle_file:
    heatloads_dict = cPickle.load(pickle_file)

with open('./heatload_pyecloud.pkl','r') as pickle_file:
    heatloads_dict_pyecloud = cPickle.load(pickle_file)

length = {}
length['ArcQuadReal'] = len_quad
length['ArcDipReal'] = dip_per_halfcell * len_dip
length['Drift'] = len_cell - length['ArcDipReal'] - length['ArcQuadReal']

hl_measured = np.empty(shape=(len(dict_keys), len(arcs)))
hl_measured_quads = np.empty(shape=(len(dict_keys), len(quads)))
for key_ctr in xrange(len(dict_keys)):
    filln = dict_keys[key_ctr][0]
    time_of_interest = dict_keys[key_ctr][1]
    model_hl_quad = heatloads_dict[filln][time_of_interest][model][0] / len_cell * len_q6
    for arc_ctr in xrange(len(arcs)):
        arc = arcs[arc_ctr]
        hl_measured[key_ctr,arc_ctr] = heatloads_dict[filln][time_of_interest][arc][0]
    for quad_ctr in xrange(len(quads)):
        quad = quads[quad_ctr]
        hl_measured_quads[key_ctr,quad_ctr] = heatloads_dict[filln][time_of_interest][quad][0] - model_hl_quad


# Functions for global

def get_heat_load(filln,time_of_interest,device,coast_str,sey_str):
    try:
        hl = heatloads_dict_pyecloud[filln][time_of_interest][device][coast_str][sey_str][0]
    except KeyError:
        print('Key error for fill %s, device %s sey %s.' % (filln+' '+time_of_interest, device, sey_str))
        return -10
    if heatloads_dict_pyecloud[filln][time_of_interest][device][coast_str][sey_str][1] == 1:
        print('Correction for fill %s, device %s sey %s coast %s.' % (filln+' '+time_of_interest, device, sey_str,coast_str))
        hl *= 2
    elif heatloads_dict_pyecloud[filln][time_of_interest][device][coast_str][sey_str][1] == 1:
        print('Error, too many entries!')
        print(filln,time_of_interest,device,coast_str,sey_str)
        sys.exit()

    return hl



def pyecloud_global(coast_str):
    if coast_str not in coast_strs:
        print('Wrong coasting beam in pyecloud_global')
        sys.exit()

    hl_pyecloud = np.zeros(shape=(len(dict_keys),len(sey_list)))

    for key_ctr in xrange(len(dict_keys)):
        for sey_ctr in xrange(len(sey_list)):
            filln = dict_keys[key_ctr][0]
            time_of_interest = dict_keys[key_ctr][1]
            sey_str = '%.2f' % sey_list[sey_ctr]
            for device in device_list:
                hl = get_heat_load(filln,time_of_interest,device,coast_str,sey_str)
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
                delta[arc_ctr,sey_ctr,1] += ((hl_measured[key_ctr,arc_ctr]-hl_pyecloud[key_ctr,sey_ctr])/hl_measured[key_ctr,arc_ctr])**2

            delta[arc_ctr,sey_ctr,1] = np.sqrt(delta[arc_ctr,sey_ctr,1])

    return delta

# Function for device

def pyecloud_device(device,coast_str):
    if device not in device_list or coast_str not in coast_str:
        print('Wrong device name in pyecloud_device!')
        sys.exit()

    hl_pyecloud = np.zeros(shape=(len(dict_keys),len(sey_list)))

    for key_ctr in xrange(len(dict_keys)):
        for sey_ctr in xrange(len(sey_list)):
            filln = dict_keys[key_ctr][0]
            time_of_interest = dict_keys[key_ctr][1]
            sey_str = '%.2f' % sey_list[sey_ctr]
            hl = get_heat_load(filln,time_of_interest,device,coast_str,sey_str)
            hl_pyecloud[key_ctr,sey_ctr] = hl

    return hl_pyecloud

def pyecloud_quad():
    hl_pyecloud = np.zeros(shape=(len(dict_keys),len(sey_list),len(coast_strs)))
    for coast_ctr in xrange(len(coast_strs)):
        hl_pyecloud[:,:,coast_ctr] = pyecloud_device('ArcQuadReal',coast_strs[coast_ctr])

    return hl_pyecloud


#Plots
one_list = np.ones(shape=sey_list.shape)

if args.g:
    fig = plt.figure()
    title_str = 'Comparison of measured to pyecloud heatloads, %i scenarios' % len(dict_keys)
    fig.canvas.set_window_title(title_str)
    plt.suptitle(title_str,fontsize=16)

    coast_subplot = (plt.subplot(2,1,1), plt.subplot(2,1,2))

    for ctr in xrange(len(coast_strs)):
        coast_str = coast_strs[ctr]
        hl_pyecloud = pyecloud_global(coast_str)
        delta = get_delta(hl_pyecloud)
        subplot = coast_subplot[ctr]

        subplot.set_ylim(0,5)
        subplot.set_title('Coasting Beam of %s' % coast_str)
        subplot.set_xlabel('SEY Parameter')
        subplot.set_ylabel('RMS deviation')


        for arc_ctr in xrange(len(arcs)):
            label = arcs[arc_ctr]
            subplot.plot(delta[arc_ctr,:,0],delta[arc_ctr,:,1],label=label)
            subplot.legend()

    plt.subplots_adjust(right=0.7, wspace=0.30)


if args.d:
    fig = plt.figure()
    title_str = 'Heatloads for different devices and scenarios, per m and scaled'
    fig.canvas.set_window_title(title_str)
    plt.suptitle(title_str,fontsize=22)

    for dev_ctr in xrange(len(device_list)):
        sp = plt.subplot(len(device_list),1,dev_ctr+1)
        device = device_list[dev_ctr]
        title = device_labels[dev_ctr]
        sp.set_title(title,fontsize=20)
        sp.grid('on')
        if dev_ctr == len(device_list)-1:
            sp.set_xlabel('SEY Parameter',fontsize=18)
        sp.set_ylabel('Heatload per m',fontsize=18)
        sp2 = sp.twinx()
        sp2.set_ylabel('Heatload per half cell',fontsize=18)
        sp2.grid('off')

        for coast_ctr in xrange(len(coast_strs)):
            coast_str = coast_strs[coast_ctr]
            data = pyecloud_device(device,coast_str)

            for sce_ctr in xrange(len(dict_keys)):
                filln_str = dict_keys[sce_ctr][0]
                time_str = dict_keys[sce_ctr][1]
                label = scenarios_labels[sce_ctr] + ' ' + coast_str + 'e9 coasting'
                sp.plot(sey_list,data[sce_ctr,:],label=label)

        if dev_ctr == 1:
            sp.legend(bbox_to_anchor=(1.1, 1),loc='upper left',fontsize=18)

        axes_factor = length[device]
        unscaled_min, unscaled_max =  sp.get_ylim()
        sp2.set_ylim(axes_factor*unscaled_min,axes_factor*unscaled_max)

    plt.subplots_adjust(right=0.75, wspace=0.25)


if args.a:
    fig = plt.figure()
    title_str = 'Fill by Fill half cell heatloads'
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
        sp.grid('on')
        sp.set_xlabel('SEY Parameter',fontsize=18)
        sp.set_ylabel('Heatload',fontsize=18)
        sp.set_title(scenarios_labels[key_ctr],fontsize=20)

        for arc_ctr in xrange(len(arcs)):
            label = arcs[arc_ctr]
            sp.plot(sey_list,hl_measured[key_ctr,arc_ctr]*one_list,'--',label=label)

        for coast_ctr in xrange(len(coast_strs)):
            coast_str = coast_strs[coast_ctr]
            label = scenarios_labels[key_ctr] + ' ' + coast_str + 'e9 coasting'
            data = datas[coast_str]
            sp.plot(sey_list,data[key_ctr,:],label=label)

        if key_ctr == 1:
            sp.legend(bbox_to_anchor=(1.1, 1),loc='upper left',fontsize=18)


if args.q:
    fig = plt.figure()
    title_str = 'Fill by Fill Q6IR5 heatloads - 8m Quadrupoles'
    fig.canvas.set_window_title(title_str)
    plt.suptitle(title_str,fontsize=20)
    plt.subplots_adjust(right=0.8, wspace=0.20)

    # Correct for QP length
    data = pyecloud_quad()*len_q6

    for key_ctr in xrange(len(dict_keys)):
        if key_ctr == 0:
            sp = plt.subplot(2,2,key_ctr+1)
        else:
            sp = plt.subplot(2,2,key_ctr+1,sharex=sp)
        sp.grid('on')
        sp.set_xlabel('SEY Parameter',fontsize=18)
        sp.set_ylabel('Totel Heatload',fontsize=18)
        sp.set_title(scenarios_labels[key_ctr],fontsize=20)

        for quad_ctr in xrange(len(quads)):
            label = quads[quad_ctr]
            sp.plot(sey_list,hl_measured_quads[key_ctr,quad_ctr]*one_list,'--',label=label)

        for coast_ctr in xrange(len(coast_strs)):
            coast_str = coast_strs[coast_ctr]
            label = coast_str + 'e9 coasting'
            sp.plot(sey_list,data[key_ctr,:,coast_ctr],label=label)

        if key_ctr == 1:
            sp.legend(bbox_to_anchor=(1.1, 1),loc='upper left',fontsize=18)


plt.show()
