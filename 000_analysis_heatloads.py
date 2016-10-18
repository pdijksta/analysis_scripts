# Written by Philipp Dijkstal, philipp.dijkstal@cern.ch

import sys
import cPickle
import argparse
import re

import matplotlib.pyplot as plt
import numpy as np

from simulation_parameters import \
        dict_keys, scenarios_labels_dict, coast_linestyle_dict, coast_strs, sey_list, devices, device_labels_dict, \
        get_filln, get_energy, get_intensity
from RcParams import init_pyplot
init_pyplot()

# Arguments

parser = argparse.ArgumentParser(description='Analysis scripts for \"SEY study arcs\".')
parser.add_argument('-p', help='Pyecloud HL for every device.', action='store_true')
parser.add_argument('-q', help='Measured and simulated HL for all Quads.', action='store_true')
parser.add_argument('-m', help='Measured data with subtracted Imp/SR heat load.', action='store_true')
parser.add_argument('-g', help='Global optimization for arcs, assumes equal SEY for all devices.', action='store_true')
parser.add_argument('-a', help='Measured and simulated HL for all Arcs, assumes equal SEY for all devices.', action='store_true')
parser.add_argument('-f', help='Full Output. Set all options above.', action='store_true')
parser.add_argument('-o', help='Dual Optimization. Assumes Drift SEY equals Arc SEY.\n\
        Devices: q, di, dr', nargs=5, metavar=('Const_device', 'SEY', 'Var_device', 'min', 'max_SEY'))
parser.add_argument('-l', help='Show vertical line for dual Optimization.', metavar='SEY', type=float, default=None, nargs='+')
parser.add_argument('-b', help='Bar plots to show the contribution of different devices to the totel heat load', metavar=('Drift SEY', 'Dipole SEY', 'Quad SEY'), nargs=3, type=float)

args = parser.parse_args()

if args.f:
    args.g = args.d = args.a = args.q = args.m = True


# Plots
plt.close('all')

# Dual optimization
if args.o:
    from d000_analysis.dual_optimization import main
    main(*args.o, args_l=args.l)

 # Global optimization
if args.g:
    import d000_analysis.global_optimization

# All devices
if args.p:
    import d000_analysis.pyecloud

# Arcs
if args.a:
    import d000_analysis.arcs

# Quadrupoles
if args.q:
    import d000_analysis.quads

# Measured
if args.m:
    import d000_analysis.measured

# Bar plots
if args.b:
    from d000_analysis.bars import main
    main(*args.b)

plt.show()
