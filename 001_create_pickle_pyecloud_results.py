import os
import sys
import cPickle
import re
import argparse

import scipy.io as sio
import numpy as np
from scipy.constants import e as const_e
from scipy.io.matlab.miobase import MatReadError

# Argparse
default_root_dir = './all_data'

parser = argparse.ArgumentParser(description='This script gathers heatloads from pyecload simulations and stores them in a pickle dict')
parser.add_argument('-d', help='Delete old pickle and build completely new one. Default: None', action='store_false')
parser.add_argument('-r', help='Root directory. Default: %s' % default_root_dir, metavar='DIR', default=default_root_dir)

args = parser.parse_args()
root_dir = args.r

if not os.path.isdir(root_dir):
    raise ValueError('DIR is not a directory')

# Config
hl_pkl_name = root_dir + '/heatload_pyecloud.pkl'
nel_hist_pkl_name = root_dir + '/nel_hist_pyecloud.pkl'
fail_name = './fail_list.txt'

if args.d:
    hl_dict = {}
    nel_hist_dict = {}
else:
    with open(hl_pkl_name,'r') as f:
        hl_dict = cPickle.load(f)
    with open(nel_hist_pkl_name,'r') as f:
        nel_hist_dict = cPickle.load(f)

all_files = os.listdir(root_dir)
# Regular Expression for the folder names
folder_re = re.compile('^Fill(\d+)_cut(\d+\.\d[1-9]*)0*h_\d+GeV_for_triplets_(B[1,2])_LHC_([A-Za-z]+)_\d+GeV_sey([\d\.]+)_coast([\d\.]+)$')

fail_ctr = 0
success_ctr = 0

fail_lines = ''
fail_lines_IO = ''
const_LHC_frev = 11.2455e3

# Functions
def insert_to_nested_dict(dictionary, value, keys, must_enter=False, add_up=False):
    """
    Inserts value to nested dictionary. The location is specified by keys.
    If must_enter is set to True, an error is raised if the entry is already present.
    """
    for key in keys[:-1]:
        if key not in dictionary:
            dictionary[key] = {}
        dictionary = dictionary[key]

    last_key = keys[-1]
    if last_key not in dictionary:
        dictionary[last_key] = value
    elif add_up:
        dictionary[last_key] += value
    elif must_enter:
        raise ValueError('Key %s already exists!' % last_key)

def check_if_already_exist(dictionary, keys):
    """
    Returns True if a nested dict with the keys in the correct order does exist.
    """
    try:
        for key in keys:
            dictionary = dictionary[key]
    except KeyError:
        return False
    else:
        return True

# Main loop
for folder in all_files:
    file_info = re.search(folder_re,folder)
    if file_info is None:
        continue

    filln = file_info.group(1)
    time_of_interest = file_info.group(2)
    beam = file_info.group(3)
    device = file_info.group(4)
    sey = file_info.group(5)
    coast = file_info.group(6)
    print(filln,time_of_interest,beam,device,sey,coast)

    # No need to keep fill and time separate
    main_key = filln + ' ' + time_of_interest
    keys = [main_key, device, coast, sey]

    if not args.d and check_if_already_exist(hl_dict, keys):
        print('Continuing for', keys)
        continue
    
    mat_str = root_dir + '/' + folder + '/Pyecltest.mat'
    if not os.path.isfile(mat_str):
        print('Warning: file %s does not exist' % mat_str)
        fail_ctr += 1
        fail_lines += folder + '\n'
        continue

    print('Trying to read %s.' % mat_str)
    try:
        matfile = sio.loadmat(mat_str)
    except (IOError, MatReadError):
        print('IOError')
        fail_ctr += 1
        fail_lines_IO += folder + '\n'
        continue
    else:
        success_ctr += 1

    heatload = np.sum(matfile['energ_eV_impact_hist'])*const_LHC_frev*const_e
    e_transverse_hist = np.sum(matfile['nel_hist'],axis=0)


    insert_to_nested_dict(hl_dict, heatload, keys+['Total'], add_up=True)
    insert_to_nested_dict(hl_dict, 1, keys+['Beam_nr'], add_up=True)
    insert_to_nested_dict(hl_dict, heatload, keys+[beam], must_enter=True)

    insert_to_nested_dict(nel_hist_dict, e_transverse_hist, keys+[beam], must_enter=True)

# add xg_hist variable only once
insert_to_nested_dict(nel_hist_dict, matfile['xg_hist'][0], ['xg_hist'], must_enter=True)

with open(hl_pkl_name, 'w') as pkl_file:
    cPickle.dump(hl_dict, pkl_file, -1)

with open(nel_hist_pkl_name, 'w') as pkl_file:
    cPickle.dump(nel_hist_dict, pkl_file, -1)

print('%i simulations were successful and %i failed.' % (success_ctr,fail_ctr))
print(fail_lines)
print('IO')
print(fail_lines_IO)

with open(fail_name,'w') as fail_file:
    fail_file.write(fail_lines)
    fail_file.write(fail_lines_IO)
