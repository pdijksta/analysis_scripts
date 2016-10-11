import numpy as np

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

sey_list = np.arange(1.1,1.51,0.05)

devices = ['ArcDipReal', 'ArcQuadReal', 'Drift']
device_labels_dict = {\
        'ArcDipReal': 'Dipole',
        'ArcQuadReal': 'Quadrupole',
        'Drift': 'Drift'
        }
