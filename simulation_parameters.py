import numpy as np
import re
import cPickle

from LHCMeasurementTools.LHC_Heatloads import magnet_length

# Parameters of the study
dict_keys = ['5219 1.8', '5222 2.3', '5223 3.0', '5219 0.92', '5222 1.63', '5223 2.3']

intensity_list = ['0.7e11', '0.9e11', '1.1e11']
energy_list = ['450GeV', '6.5TeV']

intensity_list_float = [float(string) for string in intensity_list]


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

def get_sey_ctr(get_sey, sey_list):
    for sey_ctr, sey in enumerate(sey_list):
        if round(sey,2) == float(get_sey):
            return sey_ctr
    else:
        raise ValueError('Sey %.2f could not be found!' % float(get_sey))

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


## Open pickles

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
    hl_model_arcs[key_ctr] = heatloads_dict[key][model_key]['Heat_load']
    hl_model_quads[key_ctr] = heatloads_dict[key][imp_key]['Heat_load']

    # Arcs
    for arc_ctr,arc in enumerate(arcs):
        hl_measured[key_ctr,arc_ctr] = heatloads_dict[key][arc]['Heat_load'] - heatloads_dict[key][arc]['Offset']
        arc_uncertainty[key_ctr,arc_ctr] = heatloads_dict[key][arc]['Sigma']
    hl_measured[key_ctr,:] -= hl_model_arcs[key_ctr]

    # Quads
    for quad_ctr,quad in enumerate(quads):
        # heat loads per m are needed here
        hl_pm_measured_quads[key_ctr,quad_ctr] = (heatloads_dict[key][quad]['Heat_load'] - heatloads_dict[key][quad]['Offset'])/ len_arc_quad_dict[quad]
        quad_pm_uncertainty[key_ctr,quad_ctr] = heatloads_dict[key][quad]['Sigma'] / len_arc_quad_dict[quad]

    hl_pm_measured_quads[key_ctr,:] -= hl_model_quads[key_ctr] / len_cell

# Heat load per m
hl_pm_measured = hl_measured / len_cell
hl_pm_model_arcs = hl_model_arcs / len_cell
hl_pm_model_quads = hl_model_quads / len_cell
arc_pm_uncertainty = arc_uncertainty / len_cell

# Simulation data
sey_list = np.arange(1.1,1.51,0.05)

hl_pyecloud = np.zeros(shape=(len(dict_keys),len(devices),len(coast_strs),len(sey_list)))
hl_pyecloud_beams = np.zeros(shape=(len(dict_keys),len(devices),len(coast_strs),len(sey_list),2))

for key_ctr, key in enumerate(dict_keys):
    for device_ctr, device in enumerate(devices):
        for coast_ctr, coast_str in enumerate(coast_strs):
            if device == 'Drift' and get_energy(key) == '450GeV' and not (coast_str != '0.0' and get_intensity(key) == '1.1e11'):
                # print(coast_str, get_intensity(key))
                continue
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

