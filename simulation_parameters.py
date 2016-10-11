import numpy as np
import re

# Parameters of the study
dict_keys = ['5219 1.8', '5222 2.3', '5223 3.0', '5219 0.92', '5222 1.63', '5223 2.3']

scenarios_labels_dict = {\
        '5219 1.8':  '1.1e11 6.5TeV',
        '5219 0.92': '1.1e11 450GeV',
        '5222 2.3':  '0.9e11 6.5TeV',
        '5223 3.0':  '0.7e11 6.5TeV',
        '5222 1.63': '0.9e11 450GeV',
        '5223 2.3':  '0.7e11 450GeV'
        }

#coast_strs = ['1.0', '0.5', '0.0']
coast_linestyle_dict = {\
        '1.0': '-',
        '0.5': '-.',
        '0.0': ':'
        }
coast_strs = coast_linestyle_dict.keys()
coast_strs.sort(reverse=True)

sey_list = np.arange(1.1,1.51,0.05)

devices = ['ArcDipReal', 'ArcQuadReal', 'Drift']
device_labels_dict = {\
        'ArcDipReal': 'Dipole',
        'ArcQuadReal': 'Quadrupole',
        'Drift': 'Drift'
        }

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
