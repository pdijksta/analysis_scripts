# Written by Philipp Dijkstal, philipp.dijkstal@cern.ch

import sys
import cPickle
import argparse
import re

import matplotlib.pyplot as plt
import numpy as np

from LHCMeasurementTools.LHC_Heatloads import magnet_length
from simulation_parameters import \
        dict_keys, scenarios_labels_dict, coast_linestyle_dict, coast_strs, sey_list, devices, device_labels_dict, \
        get_filln, get_energy, get_intensity
from RcParams import init_pyplot
init_pyplot()

# Arguments

arg = argparse.ArgumentParser(description='Analysis scripts for \"SEY study arcs\".')
arg.add_argument('-d', help='Simulated HL for every device.', action='store_true')
arg.add_argument('-q', help='Measured and simulated HL for all Quads.', action='store_true')
arg.add_argument('-m', help='Measured data with subtracted Imp/SR heat load.', action='store_true')
arg.add_argument('-g', help='Global optimization for arcs, assumes equal SEY for all devices.', action='store_true')
arg.add_argument('-a', help='Measured and simulated HL for all Arcs, assumes equal SEY for all devices.', action='store_true')
arg.add_argument('-f', help='Full Output. Set all options above.', action='store_true')
arg.add_argument('-o', help='Dual Optimization. Assumes Drift SEY equals Arc SEY.\n\
        Devices: q, di, dr', nargs=5, metavar=('Const_device', 'SEY', 'Var_device', 'min', 'max_SEY'))
arg.add_argument('-l', help='Show vertical line for dual Optimization.', metavar='SEY', type=float, default=None, nargs='+')
args = arg.parse_args()

if args.f:
    args.g = args.d = args.a = args.q = args.m = True

# Config

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

# Import nested dictionaries
with open('./heatload_arcs.pkl', 'r') as pickle_file:
    heatloads_dict = cPickle.load(pickle_file)

# Define arcs and quads and store their lengths
arcs = []
quads = []
len_arc_quad_dict = {}
for key in heatloads_dict[dict_keys[0]]:
    if re_arc.match(key):
        arcs.append(key)
        len_arc_quad_dict[key] = len_cell
    elif re_quad_15.match(key):
        quads.append(key)
        len_arc_quad_dict[key] = len_q6_15
    elif re_quad_28.match(key):
        quads.append(key)
        len_arc_quad_dict[key] = len_q6_28

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
        # heat loads per m are needed here
        hl_pm_measured_quads[key_ctr,quad_ctr] = heatloads_dict[key][quad][0] / len_arc_quad_dict[quad]
        quad_pm_uncertainty[key_ctr,quad_ctr] = heatloads_dict[key][quad][1] / len_arc_quad_dict[quad]

    hl_pm_measured_quads[key_ctr,:] -= hl_model_quads[key_ctr] / len_cell

# Heat load per m
hl_pm_measured = hl_measured / len_cell
hl_pm_model_arcs = hl_model_arcs / len_cell
hl_pm_model_quads = hl_model_quads / len_cell
arc_pm_uncertainty = arc_uncertainty / len_cell

# Simulation data
hl_pyecloud = np.zeros(shape=(len(dict_keys),len(devices),len(coast_strs),len(sey_list)))
hl_pyecloud_beams = np.zeros(shape=(len(dict_keys),len(devices),len(coast_strs),len(sey_list),2))

for key_ctr, key in enumerate(dict_keys):
    for device_ctr, device in enumerate(devices):
        if device == 'Drift' and get_energy(key) == '450GeV':
            # No E-Cloud expected here!
            hl_pyecloud[key_ctr,device_ctr,:,:] = 0
            continue
        for coast_ctr, coast_str in enumerate(coast_strs):
            for sey_ctr, sey in enumerate(sey_list):
                sey_str = '%.2f' % sey
                try:
                    hl = heatloads_dict_pyecloud[key][device][coast_str][sey_str]['Total']
                except KeyError:
                    print('Key error for fill %s, device %s sey %s coast %s.' % (key, device, sey_str, coast_str))
                else:
                    # If no sim data for one beam, double the heatload from the other beam
                    if heatloads_dict_pyecloud[key][device][coast_str][sey_str]['Beam_nr'] == 1:
                        print('Correction for fill %s, device %s sey %s coast %s.' % (key, device, sey_str, coast_str))
                        hl *= 2

                    hl_pyecloud[key_ctr,device_ctr,coast_ctr,sey_ctr] += hl
                try:
                    hl_b1 = heatloads_dict_pyecloud[key][device][coast_str][sey_str]['B1']
                    hl_pyecloud_beams[key_ctr,device_ctr,coast_ctr,sey_ctr,0] = hl_b1
                except KeyError:
                    print('Key error for fill %s, device %s sey %s coast %s beam %s' % (key, device, sey_str, coast_str,'B1'))
                try:
                    hl_b2 = heatloads_dict_pyecloud[key][device][coast_str][sey_str]['B2']
                    hl_pyecloud_beams[key_ctr,device_ctr,coast_ctr,sey_ctr,1] = hl_b2
                except KeyError:
                    print('Key error for fill %s, device %s sey %s coast %s beam %s' % (key, device, sey_str, coast_str,'B2'))

# Plots
plt.close('all')
one_list = np.ones_like(sey_list)

# Dual optimization
if args.o:
    from d000_analysis.dual_optimization import main
    main(hl_pyecloud, devices, coast_strs, scenarios_labels_dict, length, dict_keys,
            arcs, hl_measured, sey_list, args.l, args.o, device_labels_dict, get_energy)

 # Global optimization
if args.g:
    from d000_analysis.global_optimization import main
    main(dict_keys,arcs,sey_list,coast_strs,hl_pm_measured,hl_pyecloud, length, devices)

# All devices
if args.d:
    from d000_analysis.devices import main
    main(devices,device_labels_dict, sey_list, coast_strs, dict_keys, hl_pyecloud, scenarios_labels_dict, length, coast_linestyle_dict, get_energy, get_intensity)

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
            get_intensity, get_energy, hl_pm_model_arcs, hl_pm_model_quads, arc_pm_uncertainty, quad_pm_uncertainty, len_arc_quad_dict)

plt.show()
