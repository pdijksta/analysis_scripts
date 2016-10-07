# Written by Philipp Dijkstal, philipp.dijkstal@cern.ch

import sys
import cPickle
import argparse
import re

import matplotlib.pyplot as plt
import numpy as np
import math

from LHCMeasurementTools.LHC_Heatloads import magnet_length
from RcParams import init_pyplot
init_pyplot()

# Arguments

arg = argparse.ArgumentParser(description='')
arg.add_argument('-d', help='Simulated HL for every device.', action='store_true')
arg.add_argument('-q', help='Measured and simulated HL for all Quads.', action='store_true')
arg.add_argument('-m', help='Measured data with subtracted Imp/SR heat load.', action='store_true')
arg.add_argument('-o', help='Dual Optimization. Assumes Drift SEY equals Arc SEY', action='store_true')
arg.add_argument('-g', help='Global optimization for arcs, assumes equal SEY for all devices.', action='store_true')
arg.add_argument('-a', help='Measured and simulated HL for all Arcs, assumes equal SEY for all devices.', action='store_true')
arg.add_argument('-f', help='Full Output. Set all other options to true.', action='store_true')
args = arg.parse_args()

if args.f:
    args.g = args.d = args.a = args.q = args.o = args.m = True

# Config

# Parameters of the study
dict_keys = ['5219 1.8', '5222 2.3', '5223 3.0', '5219 0.92', '5222 1.63', '5223 2.3']
print('Scenarios:\n' + str(dict_keys))

scenarios_labels_dict = {\
        '5219 1.8':  '1.1e11 6.5TeV',
        '5219 0.92': '1.1e11 450GeV',
        '5222 2.3':  '0.9e11 6.5TeV',
        '5223 3.0':  '0.7e11 6.5TeV',
        '5222 1.63': '0.9e11 450GeV',
        '5223 2.3':  '0.7e11 450GeV'
        }

coast_strs = ['1.0', '0.5', '0.0']
coast_linestyle_dict = {\
        '1.0': '-',
        '0.5': '-.',
        '0.0': ':'
        }

sey_list = np.arange(1.1,1.51,0.05)

devices = ['ArcDipReal', 'ArcQuadReal', 'Drift']
device_labels_dict = {\
        'ArcDipReal': 'Dipole',
        'ArcQuadReal': 'Quadrupole',
        'Drift': 'Drift'
        }

# Names of devices, regular expressions
re_arc = re.compile('^S\d\d$')
re_quad = re.compile('^Q06[LR][1258]$')
re_quad_15 = re.compile('^Q06[LR][15]$')
re_quad_28 = re.compile('^Q06[LR][28]$')

model_key = 'Imp+SR'
imp_key = 'Imp'
#sr_key = 'SR' # not needed

# Lengths from dictionary
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

# Obtain info from scenarios_labels_dict
re_filln = re.compile('^(\d{4})')
def get_filln(key):
    info = re.search(re_filln,key)
    return info.group(1)

re_energy = re.compile('([\d\.]{3}[GT]eV)')
def get_energy(key):
    label = scenarios_labels_dict[key]
    info = re.search(re_energy,label)
    return info.group(1)

re_intensity = re.compile('^(\d\.\de\d\d)')
def get_intensity(key):
    label = scenarios_labels_dict[key]
    info = re.search(re_intensity,label)
    return info.group(1)

# Import nested dictionaries
with open('./heatload_arcs.pkl', 'r') as pickle_file:
    heatloads_dict = cPickle.load(pickle_file)

# Define arcs and quads
arcs = []
quads = []
for key in heatloads_dict[dict_keys[0]].keys():
    if re_arc.match(key):
        arcs.append(key)
    elif re_quad.match(key):
        quads.append(key)

with open('./heatload_pyecloud.pkl', 'r') as pickle_file:
    heatloads_dict_pyecloud = cPickle.load(pickle_file)

# Measured data
hl_measured = np.empty(shape=(len(dict_keys),len(arcs)))
hl_pm_measured_quads = np.empty(shape=(len(dict_keys),len(quads)))

hl_model_arcs = np.empty(shape=(len(dict_keys),))
hl_model_quads = np.copy(hl_model_arcs)

arc_uncertainty = np.empty_like(hl_measured)
quad_pm_uncertainty = np.empty_like(hl_pm_measured_quads)

for key_ctr, key in enumerate(dict_keys):
    # Model
    hl_model_arcs[key_ctr] = heatloads_dict[key][model_key][0]
    hl_model_quads[key_ctr] = heatloads_dict[key][imp_key][0]

    # Arcs
    for arc_ctr,arc in enumerate(arcs):
        hl_measured[key_ctr,arc_ctr] = heatloads_dict[key][arc][0] - heatloads_dict[key][arc][2]
        arc_uncertainty[key_ctr,arc_ctr] = heatloads_dict[key][arc][1]
    hl_measured[key_ctr,:] -= hl_model_arcs[key_ctr]

    # Quads
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
        quad_pm_uncertainty[key_ctr,quad_ctr] = heatloads_dict[key][quad][1] / length_quad

    hl_pm_measured_quads[key_ctr,:] -= hl_model_quads[key_ctr] / len_cell

# Heat load per m
hl_pm_measured = hl_measured / len_cell
hl_pm_model_arcs = hl_model_arcs / len_cell
hl_pm_model_quads = hl_model_quads / len_cell
arc_pm_uncertainty = arc_uncertainty / len_cell

# Simulation data
# Sum over beam 1 and 2
hl_pyecloud = np.zeros(shape=(len(dict_keys),len(devices),len(coast_strs),len(sey_list)))
for key_ctr, key in enumerate(dict_keys):
    for device_ctr, device in enumerate(devices):
        if device == 'Drift' and get_energy(key) == '450GeV':
            hl_pyecloud[key_ctr,device_ctr,:,:] = 0
            continue
        for coast_ctr, coast_str in enumerate(coast_strs):
            for sey_ctr, sey in enumerate(sey_list):
                sey_str = '%.2f' % sey
                hl = 0
                try:
                    hl = heatloads_dict_pyecloud[key][device][coast_str][sey_str][0]
                except KeyError:
                    print('Key error for fill %s, device %s sey %s coast %s.' % (key, device, sey_str, coast_str))
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
    main(dict_keys,arcs,sey_list,coast_strs,hl_pm_measured,hl_pyecloud, length, devices)

# All devices
if args.d:
    from d000_analysis.devices import main
    main(devices,device_labels_dict, sey_list, coast_strs, dict_keys, hl_pyecloud, scenarios_labels_dict, length, coast_linestyle_dict)

# Arcs
if args.a:
    from d000_analysis.arcs import main
    main(hl_pyecloud, hl_measured, length, arc_uncertainty, scenarios_labels_dict, arcs, sey_list, coast_strs, dict_keys, devices,coast_linestyle_dict)

# Quadrupoles
if args.q:
    from d000_analysis.quads import main
    main(devices, coast_strs, hl_pyecloud, hl_pm_measured_quads, dict_keys, quad_pm_uncertainty, quads, sey_list, scenarios_labels_dict, coast_linestyle_dict)

# Measured
if args.m:
    from d000_analysis.measured import main
    main(hl_pm_measured, hl_pm_measured_quads, dict_keys, arcs, quads, scenarios_labels_dict,
            get_intensity, get_energy, hl_pm_model_arcs, hl_pm_model_quads, arc_pm_uncertainty, quad_pm_uncertainty)

plt.show()
