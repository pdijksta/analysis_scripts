# This script gathers heatloads from pyecload simulations and stores them in a pickle dict

import os
import sys
import cPickle
import re

import scipy.io as sio
import numpy as np
from scipy.constants import e as const_e

# Config

root_dir = './all_data'

hl_dict = {}
all_files = os.listdir(root_dir)
# Regular Expression for the folder names
folder_re = re.compile('^Fill(\d+)_cut(\d+\.\d[1-9]*)0*h_\d+GeV_for_triplets_(B[1,2])_LHC_([A-Za-z]+)_\d+GeV_sey([\d\.]+)_coast([\d\.]+)$')

fail_ctr = 0
success_ctr = 0

fail_lines = ''
fail_lines_IO = ''
const_LHC_frev = 11.2455e3

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


for folder in all_files:
    file_info = re.search(folder_re,folder)
    if file_info is None:
        continue

    filln = file_info.group(1)
    time_of_interest = file_info.group(2)
    main_key = filln + ' ' + time_of_interest
    beam = file_info.group(3)
    device = file_info.group(4)
    sey = file_info.group(5)
    coast = file_info.group(6)
    print(filln,time_of_interest,beam,device,sey,coast)

    mat_str = root_dir + '/' + folder + '/Pyecltest.mat'
    if not os.path.isfile(mat_str):
        print('Warning: file %s does not exist' % mat_str)
        fail_ctr += 1
        fail_lines += folder + '\n'
        continue


    print('Trying to read %s.' % mat_str)
    try:
        matfile = sio.loadmat(mat_str)
    except IOError:
        print('IOError')
        fail_ctr += 1
        fail_lines_IO += folder + '\n'
        continue
    else:
        success_ctr += 1

    heatload = np.sum(matfile['energ_eV_impact_hist'])*const_LHC_frev*const_e
#    e_transverse_hist = np.sum(matfile['nel_hist'],axis=0)
#    print(e_transverse_hist)
#    sys.exit()

    insert_to_nested_dict(hl_dict, heatload, [main_key,device,coast,sey,'Total'], add_up=True)
    insert_to_nested_dict(hl_dict, 1, [main_key,device,coast,sey,'Beam_nr'], add_up=True)
    insert_to_nested_dict(hl_dict, heatload, [main_key, device, coast, sey, beam], must_enter=True)

print(hl_dict)

#with open('./heatload_pyecloud.pkl','w') as pkl:
#    cPickle.dump(hl_dict,pkl)

print(fail_ctr, success_ctr)
print(fail_lines)
print('IO')
print(fail_lines_IO)

with open('./fail_list.txt','w') as fail_file:
    fail_file.write(fail_lines)
    fail_file.write(fail_lines_IO)
