import numpy as np
import TimberManager as tm

class Heatload:
    def __init__(self, timber_variable, sector):

        if type(timber_variable) is str:
            dict_timber = tm.parse_timber_file(timber_variable, verbose=True)
            timber_variable_hl = dict_timber[get_variable_dict(sector)['ARC_AVG']]

        elif type(timber_variable) is dict:
            timber_variable_hl = timber_variable[get_variable_dict(sector)['ARC_AVG']]

        # print np.squeeze(np.array(timber_variable_hl.values)).shape
        # print np.squeeze(np.array(timber_variable_hl.values))

        self.t_stamps = np.float_(np.array(timber_variable_hl.t_stamps))
        self.hl = np.squeeze(np.float_(np.array(timber_variable_hl.values)))



def get_variable_dict(sector):
    var_dict = {}
    var_dict['ARC_AVG'] = 'S%d_QBS_AVG_ARC.POSST'%sector

    return var_dict

def variable_list(sectors=[12,23,34,45,56,67,78,81]):
    var_list = []
    for sector in sectors:
        var_list += get_variable_dict(sector).values()

    return var_list

def sector_list():
    sector_list = [12,23,34,45,56,67,78,81]

    return sector_list


def arc_average_correction_factors():
    corr_factors = [1.3, 1.24, 1.22, 1.28, 1.26, 1.22, 1.24, 1.3]

    return corr_factors


average_arcs_variable_list = variable_list
variable_lists_heatloads = {}

variable_lists_heatloads['AVG_ARC'] = average_arcs_variable_list()

variable_lists_heatloads['Q4D2s_IR1'] = 'QRLFD_04L1_QBS947.POSST QRLFC_04R1_QBS947.POSST'.split()
variable_lists_heatloads['Q4D2s_IR5'] = 'QRLFC_04L5_QBS947.POSST QRLFD_04R5_QBS947.POSST'.split()
variable_lists_heatloads['Q4D2s_IR2'] = 'QRLFE_04L2_QBS947.POSST QRLFF_04R2_QBS947.POSST'.split()
variable_lists_heatloads['Q4D2s_IR8'] = 'QRLFE_04L8_QBS947.POSST QRLFF_04R8_QBS947.POSST'.split()

variable_lists_heatloads['Q6s_IR1'] = 'QRLEC_06L1_QBS947.POSST QRLEC_06R1_QBS947.POSST'.split()
variable_lists_heatloads['Q6s_IR5'] = 'QRLEC_06L5_QBS947.POSST QRLEC_06R5_QBS947.POSST'.split()
variable_lists_heatloads['Q6s_IR2'] = 'QRLEA_06L2_QBS947.POSST QRLEA_06R2_QBS947.POSST'.split()
variable_lists_heatloads['Q6s_IR8'] = 'QRLEA_06L8_QBS947.POSST QRLDE_06R8_QBS947.POSST'.split()

variable_lists_heatloads['Q5s_IR1'] = 'QRLEC_05L1_QBS947.POSST QRLEC_05R1_QBS947.POSST'.split()
variable_lists_heatloads['Q5s_IR5'] = 'QRLEC_05L5_QBS947.POSST QRLEC_05R5_QBS947.POSST'.split()
variable_lists_heatloads['Q5s_IR2'] = 'QRLEA_05L2_QBS947.POSST QRLEA_05R2_QBS947.POSST'.split()
variable_lists_heatloads['Q5s_IR8'] = 'QRLEA_05L8_QBS947.POSST QRLEA_05R8_QBS947.POSST'.split()

variable_lists_heatloads['IT_IR1'] = 'QRLGA_03L1_QBS947.POSST QRLGC_03R1_QBS947.POSST'.split()
variable_lists_heatloads['IT_IR5'] = 'QRLGD_03L5_QBS947.POSST QRLGB_03R5_QBS947.POSST'.split()
variable_lists_heatloads['IT_IR2'] = 'QRLGF_03L2_QBS947.POSST QRLGE_03R2_QBS947.POSST'.split()
variable_lists_heatloads['IT_IR8'] = 'QRLGF_03L8_QBS947.POSST QRLGE_03R8_QBS947.POSST'.split()

variable_lists_heatloads['special_HC_Q1'] = 'QRLAA_13L5_QBS943_Q1.POSST QRLAA_33L5_QBS947_Q1.POSST QRLAA_13R4_QBS947_Q1.POSST'.split()
variable_lists_heatloads['special_HC_D2'] = 'QRLAA_13L5_QBS943_D2.POSST QRLAA_13R4_QBS947_D2.POSST QRLAA_33L5_QBS947_D2.POSST'.split()
variable_lists_heatloads['special_HC_D3'] = 'QRLAA_13L5_QBS943_D3.POSST QRLAA_13R4_QBS947_D3.POSST QRLAA_33L5_QBS947_D3.POSST'.split()
variable_lists_heatloads['special_HC_D4'] = 'QRLAA_13R4_QBS947_D4.POSST QRLAA_33L5_QBS947_D4.POSST QRLAA_13L5_QBS943_D4.POSST'.split()
variable_lists_heatloads['special_total'] = 'QRLAA_13R4_QBS947.POSST QRLAA_33L5_QBS947.POSST QRLAA_13L5_QBS943.POSST'.split()

variable_lists_heatloads['MODEL'] = ['LHC.QBS_CALCULATED_ARC_IMPED.B1', 'LHC.QBS_CALCULATED_ARC_IMPED.B2',
                                     'LHC.QBS_CALCULATED_ARC_SYNCH_RAD.B1', 'LHC.QBS_CALCULATED_ARC_SYNCH_RAD.B2',
                                     'LHC.QBS_CALCULATED_ARC.TOTAL']

def groups_dict():
    dict_hl_groups = {}
    dict_hl_groups['InnerTriplets'] = variable_lists_heatloads['IT_IR1']+variable_lists_heatloads['IT_IR5']+\
        variable_lists_heatloads['IT_IR2']+variable_lists_heatloads['IT_IR8']
    dict_hl_groups['Arcs'] = variable_lists_heatloads['AVG_ARC']
    dict_hl_groups['Q5s'] = variable_lists_heatloads['Q5s_IR1']+variable_lists_heatloads['Q5s_IR5']+\
        variable_lists_heatloads['Q5s_IR2']+variable_lists_heatloads['Q5s_IR8']
    dict_hl_groups['Q6s'] = variable_lists_heatloads['Q6s_IR1']+variable_lists_heatloads['Q6s_IR5']+\
        variable_lists_heatloads['Q6s_IR2']+variable_lists_heatloads['Q6s_IR8']
    dict_hl_groups['Q4D2s'] =  variable_lists_heatloads['Q4D2s_IR1']+ variable_lists_heatloads['Q4D2s_IR5']+\
        variable_lists_heatloads['Q4D2s_IR2']+ variable_lists_heatloads['Q4D2s_IR8']

    dict_hl_groups['special_HC_Q1']	= variable_lists_heatloads['special_HC_Q1']
    dict_hl_groups['special_HC_dipoles'] = variable_lists_heatloads['special_HC_D2']+\
        variable_lists_heatloads['special_HC_D3']+variable_lists_heatloads['special_HC_D4']
#    dict_hl_groups['special_HC_total'] = variable_lists_heatloads['special_total']

    return dict_hl_groups


cryogenic_length = {}

cryogenic_length['AVG_ARC'] = [53.45]
cryogenic_length['MODEL'] = [53.45]

cryogenic_length['Q4D2s_IR1'] = [19.4]
cryogenic_length['Q4D2s_IR5'] = [19.4]
cryogenic_length['Q4D2s_IR2'] = [22.8]
cryogenic_length['Q4D2s_IR8'] = [22.8]

cryogenic_length['Q6s_IR1'] = [8.2]
cryogenic_length['Q6s_IR5'] = [8.2]
cryogenic_length['Q6s_IR2'] = [12.]
cryogenic_length['Q6s_IR8'] = [12.]

cryogenic_length['Q5s_IR1'] = [8.2]
cryogenic_length['Q5s_IR5'] = [8.2]
cryogenic_length['Q5s_IR2'] = [13.]
cryogenic_length['Q5s_IR8'] = [13.]

cryogenic_length['IT_IR1'] = [40.]
cryogenic_length['IT_IR5'] = [40.]
cryogenic_length['IT_IR2'] = [50.]
cryogenic_length['IT_IR8'] = [50.]

cryogenic_length['special_HC_Q1'] = [3.1]
cryogenic_length['special_HC_D2'] = [14.3]
cryogenic_length['special_HC_D3'] = [14.3]
cryogenic_length['special_HC_D4'] = [14.3]
cryogenic_length['special_total'] = [53.45]


magnet_length = {}

magnet_length['AVG_ARC'] = [53.45]
magnet_length['MODEL'] = [53.45]
magnet_length['Q4D2s_IR1'] = [18.08]
magnet_length['Q4D2s_IR5'] = [18.08]
magnet_length['Q4D2s_IR2'] = [21.39]
magnet_length['Q4D2s_IR8'] = [21.39]

magnet_length['Q6s_IR1'] = [4.8]
magnet_length['Q6s_IR5'] = [4.8]
magnet_length['Q6s_IR2'] = [8.567]
magnet_length['Q6s_IR8'] = [8.567]

magnet_length['Q5s_IR1'] = [4.8]
magnet_length['Q5s_IR5'] = [4.8]
magnet_length['Q5s_IR2'] = [7.181]
magnet_length['Q5s_IR8'] = [7.181]

magnet_length['IT_IR1'] = [36.98]
magnet_length['IT_IR5'] = [36.96]
magnet_length['IT_IR2'] = [44.91]
magnet_length['IT_IR8'] = [44.91]

magnet_length['special_HC_Q1'] = [3.1]
magnet_length['special_HC_D2'] = [14.3]
magnet_length['special_HC_D3'] = [14.3]
magnet_length['special_HC_D4'] = [14.3]
magnet_length['special_total'] = [53.45]


def groups_length_dict(length='cryogenic_length'):

    name_dict = variable_lists_heatloads

    if length == 'magnet_length':
        len_dict = magnet_length
    elif length == 'cryogenic_length':
        len_dict = cryogenic_length

    dict_len_groups = {}

    dict_len_groups['InnerTriplets'] = []
    dict_len_groups['Arcs'] = []
    dict_len_groups['Q5s'] = []
    dict_len_groups['Q6s'] = []
    dict_len_groups['Q4D2s'] = []
    dict_len_groups['special_HC_Q1'] = []
    dict_len_groups['special_HC_dipoles'] = [] 
    dict_len_groups['special_HC_total'] = []


    dict_len_groups['InnerTriplets'].extend(len_dict['IT_IR1']*len(name_dict['IT_IR1']))
    dict_len_groups['InnerTriplets'].extend(len_dict['IT_IR5']*len(name_dict['IT_IR5']))
    dict_len_groups['InnerTriplets'].extend(len_dict['IT_IR2']*len(name_dict['IT_IR2']))
    dict_len_groups['InnerTriplets'].extend(len_dict['IT_IR8']*len(name_dict['IT_IR8']))

    dict_len_groups['Arcs'].extend(len_dict['AVG_ARC']*len(name_dict['AVG_ARC']))

    dict_len_groups['Q5s'].extend(len_dict['Q5s_IR1']*len(name_dict['Q5s_IR1']))
    dict_len_groups['Q5s'].extend(len_dict['Q5s_IR5']*len(name_dict['Q5s_IR5']))
    dict_len_groups['Q5s'].extend(len_dict['Q5s_IR2']*len(name_dict['Q5s_IR2']))
    dict_len_groups['Q5s'].extend(len_dict['Q5s_IR8']*len(name_dict['Q5s_IR8']))

    dict_len_groups['Q6s'].extend(len_dict['Q6s_IR1']*len(name_dict['Q6s_IR1']))
    dict_len_groups['Q6s'].extend(len_dict['Q6s_IR5']*len(name_dict['Q6s_IR5']))
    dict_len_groups['Q6s'].extend(len_dict['Q6s_IR2']*len(name_dict['Q6s_IR2']))
    dict_len_groups['Q6s'].extend(len_dict['Q6s_IR8']*len(name_dict['Q6s_IR8']))

    dict_len_groups['Q4D2s'].extend(len_dict['Q4D2s_IR1']*len(name_dict['Q4D2s_IR1']))
    dict_len_groups['Q4D2s'].extend(len_dict['Q4D2s_IR5']*len(name_dict['Q4D2s_IR5']))
    dict_len_groups['Q4D2s'].extend(len_dict['Q4D2s_IR2']*len(name_dict['Q4D2s_IR2']))
    dict_len_groups['Q4D2s'].extend(len_dict['Q4D2s_IR8']*len(name_dict['Q4D2s_IR8']))

    dict_len_groups['special_HC_Q1'].extend(len_dict['special_HC_Q1']*len(name_dict['special_HC_Q1']))
    dict_len_groups['special_HC_dipoles'].extend(len_dict['special_HC_D2']*len(name_dict['special_HC_D2']))
    dict_len_groups['special_HC_dipoles'].extend(len_dict['special_HC_D3']*len(name_dict['special_HC_D3']))
    dict_len_groups['special_HC_dipoles'].extend(len_dict['special_HC_D4']*len(name_dict['special_HC_D4']))

#    dict_len_groups['special_HC_total'].extend(len_dict['special_total']*len(name_dict['special_total']))

    return dict_len_groups


def sector_all_variables(sectors):
    sectors = np.array(sectors, ndmin=1)
    
    sector_variable_list = []
    for sector in sectors:
        sector_R = str(sector)[0]
        sector_L = str(sector)[1]

        variable_list_R = ['QRLBA_09R','QRLAB_11R','QRLAA_13R','QRLAB_15R','QRLAA_17R','QRLAB_19R','QRLAA_21R',
                           'QRLAB_23R','QRLAA_25R','QRLAB_27R','QRLAA_29R','QRLAC_31R','QRLAD_33R']
        variable_list_L = ['QRLAA_33L','QRLAB_31L','QRLAA_29L','QRLAB_27L','QRLAA_25L','QRLAB_23L','QRLAA_21L',
                           'QRLAB_19L','QRLAA_17L','QRLAB_15L','QRLAA_13L','QRLAB_11L','QRLBA_09L', 
                           'QRLBB_09L','QRLAH_11L','QRLAG_13L','QRLAH_15L','QRLAG_17L','QRLAF_25L','QRLAE_25L']#this line is for special cases
    
        for variable in variable_list_R:
            for nqbs in [943,947]:
                curr_variable = variable+'%s_QBS%d.POSST'%(sector_R, nqbs)
                sector_variable_list.append(curr_variable)
        for variable in variable_list_L:
            for nqbs in [947,943]:
                curr_variable = variable+'%s_QBS%d.POSST'%(sector_L, nqbs)
                sector_variable_list.append(curr_variable)

    return sector_variable_list
    
def get_dict_magnet_lengths():
    dict_lengths = {}
    for kk in variable_lists_heatloads.keys():
        for device in variable_lists_heatloads[kk]:
            dict_lengths[device] = magnet_length[kk][0]
    return dict_lengths
    
def get_dict_cryostat_lengths():
    dict_lengths = {}
    for kk in variable_lists_heatloads.keys():
        for device in variable_lists_heatloads[kk]:
            dict_lengths[device] = cryogenic_length[kk][0]
    return dict_lengths


