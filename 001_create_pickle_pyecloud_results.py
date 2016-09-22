# This script gathers heatloads from pyecload simulations and stores them in a pickle dict

import os
import sys
import cPickle
import re

import scipy.io as sio
import numpy as np
from scipy.constants import e as const_e

const_LHC_frev = 11.2455e3
root_dir = './all_data'

hl_dict = {}
all_files = os.listdir(root_dir)
file_re = re.compile('^Fill(\d+)_cut(\d+\.\d[1-9]*)0*h_\d+GeV_for_triplets_(B[1,2])_LHC_([A-Za-z]+)_\d+GeV_sey([\d\.]+)_coast([\d\.]+)$')

fail_ctr = 0
success_ctr = 0

fail_lines = ''
fail_lines_IO = ''

for f in all_files:
    file_info = re.search(file_re,f)
    if file_info is None:
        continue


    filln = file_info.group(1)
    time_of_interest = file_info.group(2)
    beam = file_info.group(3)
    device = file_info.group(4)
    sey = file_info.group(5)
    coast = file_info.group(6)
    print(filln,time_of_interest,beam,device,sey,coast)

    mat_str = root_dir + '/' + f + '/Pyecltest.mat'
    if not os.path.isfile(mat_str):
        print('Warning: file %s does not exist' % mat_str)
        fail_ctr += 1
        fail_lines += f + '\n'
        continue


    print('Trying to read %s.' % mat_str)
    try:
        matfile = sio.loadmat(mat_str)
    except IOError:
        print('IOError')
        fail_ctr += 1
        fail_lines_IO += f + '\n'
        continue
    else:
        success_ctr += 1

    heatload = np.sum(matfile['energ_eV_impact_hist'])*const_LHC_frev*const_e

    if filln not in hl_dict.keys():
        hl_dict[filln] = {}
    if time_of_interest not in hl_dict[filln].keys():
        hl_dict[filln][time_of_interest] = {}
    if device not in hl_dict[filln][time_of_interest].keys():
        hl_dict[filln][time_of_interest][device] = {}
    if coast not in hl_dict[filln][time_of_interest][device].keys():
        hl_dict[filln][time_of_interest][device][coast] = {}
    if sey not in  hl_dict[filln][time_of_interest][device][coast].keys():
        hl_dict[filln][time_of_interest][device][coast][sey] = [0, 0]
        
    # add up Beams 1 and 2 
    hl_dict[filln][time_of_interest][device][coast][sey][0] += heatload
    hl_dict[filln][time_of_interest][device][coast][sey][1] += 1

#print(hl_dict)

with open('./heatload_pyecloud.pkl','w') as pkl:
    cPickle.dump(hl_dict,pkl)

print(fail_ctr, success_ctr)
print(fail_lines)
print('IO')
print(fail_lines_IO)

with open('./fail_list.txt','w') as fail_file:
    fail_file.write(fail_lines)
    fail_file.write(fail_lines_IO)
