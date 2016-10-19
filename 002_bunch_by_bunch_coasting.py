import sys
import argparse

import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
from scipy.constants import e as qe

import LHCMeasurementTools.myfilemanager as mlo
import LHCMeasurementTools.mystyle as ms
from LHCMeasurementTools.LHC_Heatloads import magnet_length

from RcParams import init_pyplot
init_pyplot()

parser = argparse.ArgumentParser(description=\
        'Show bunch by bunch power losses from PyECLOUD simulations and measurements.')

parser.add_argument('q', help='Assumed quadrupole SEY', metavar='Quad SEY', type=float)
parser.add_argument('d', help='Assumed drift SEY', metavar='Drift SEY', type=float)
parser.add_argument('beam', help='B1 | B2', type=str, metavar='Beam')
parser.add_argument('filln', help='5219 | 5222 | 5223', type=str, metavar='Fill')
parser.add_argument('energy', help='450 | 6500', type=str, metavar='Energy')
args = parser.parse_args()

assumed_quad_sey = args.q
assumed_drift_sey = args.d
beam = args.beam
filln = args.filln
energy = args.energy

if beam == 'B1':
    colorbeam = 'b'
elif beam == 'B2':
    colorbeam = 'r'
else:
    raise ValueError('Incorrect specification of beam!')

T_rev = 88.9e-6

main_folder = './all_data'
beam_snapshot_folder = './beam_snapshots'

machine_name = 'LHC'
devices = ['Drift', 'ArcDipReal', 'ArcQuadReal']

coast_strs = ['1.0', '0.5', '0.0']
coast_linestyle_dict = {\
        '1.0': '-',
        '0.5': '-.',
        '0.0': ':'
        }

l_hc = magnet_length['AVG_ARC'][0]
l_dip = 3 * magnet_length['special_HC_D2'][0]
l_quad = magnet_length['special_HC_Q1'][0]
l_drift = l_hc - l_dip - l_quad

beam_snapshot_dict = {'5219': {}, '5222': {}, '5223': {}}
beam_snapshot_dict['5219']['450'] = '0.920'
beam_snapshot_dict['5219']['6500'] = '1.800'
beam_snapshot_dict['5222']['450'] = '1.630'
beam_snapshot_dict['5222']['6500'] = '2.300'
beam_snapshot_dict['5223']['450'] = '2.300'
beam_snapshot_dict['5223']['6500'] = '3.000'

time = beam_snapshot_dict[filln][energy]

beam_snapshot = 'Fill%s_cut%sh_%sGeV_for_triplets_%s.mat' % (filln, time, energy, beam)

ob_snapshot = mlo.myloadmat_to_obj(beam_snapshot_folder+'/'+beam_snapshot)
meas_loss_per_meter = ob_snapshot.bunch_power_loss/23./2./8./l_hc
meas_loss_per_hc = meas_loss_per_meter * l_hc

sey_vect = np.arange(1.10,1.501,.05)
N_sims = len(sey_vect)

def get_simulation_ob(device_name, sey, coast_str='0.5'):

    sim_ident = '%s_%s_%s_%s_sey%.2f_coast%s' % (beam_snapshot.split('.mat')[0], machine_name, device_name, energy+'GeV', sey, coast_str)
    ob = mlo.myloadmat_to_obj(main_folder + '/' + sim_ident+'/Pyecltest.mat')
    # from Gianni
    t_bun = np.arange(0.,np.max(ob.t),  ob.b_spac)
    L_imp_t = np.cumsum(ob.En_imp_eV_time-ob.En_emit_eV_time); #in eV
    L_imp = np.interp(t_bun, ob.t, L_imp_t) #in eV
    Ek = np.interp(t_bun, ob.t, ob.En_kin_eV_time);
    sim_loss_per_meter = (np.diff(L_imp) + np.diff(Ek))*qe/T_rev; #watt/m

    return sim_loss_per_meter, ob, t_bun

try:
    quad_contribution_per_meter, quad_ob,t_bun = get_simulation_ob('ArcQuadReal', assumed_quad_sey)
except IOError:
    quad_contribution_per_meter = 0
try:
    drift_contribution_per_meter, drift_ob,t_bun = get_simulation_ob('Drift', assumed_drift_sey)
except IOError:
    drift_contribution_per_meter = 0

quad_contribution_per_hc = quad_contribution_per_meter * l_quad
drift_contribution_per_hc = drift_contribution_per_meter * l_drift

plt.close('all')

###
fig = plt.figure()
title_str = 'Electrons and protons in the machine'
fig.canvas.set_window_title(title_str)
plt.suptitle(title_str, fontsize=25)

sp0 = plt.subplot(2,1,1)
sp0.plot(ob_snapshot.ppb_vect, color=colorbeam,label='Measured')
sp0.set_ylabel('Bunch intensity [p$^+$]')
sp0.set_xlim(0,3500)

sp_el = plt.subplot(2,1,2, sharex=sp0)
sp_el.set_ylabel('Electrons [1/m]')

###
fig = plt.figure()
title_str = 'Comparison of measured to simulated bunch by bunch power losses %s.' % args.beam
fig.canvas.set_window_title(title_str)
title_str += '\nAssumed Quad/Drift SEY: %.2f/%.2f' % (assumed_quad_sey,assumed_drift_sey)
plt.suptitle(title_str, fontsize=25)

t_bun_zeros = np.zeros_like(t_bun[:-1])
t_bun_ones = np.ones_like(t_bun_zeros)

sp = None
for coast_ctr, coast_str in enumerate(coast_strs):
    sp = plt.subplot(3,1,coast_ctr+1, sharex=sp)
    sp.set_ylabel('Power loss [W/hc]')
    sp.plot(meas_loss_per_hc, '.-', color='k', label='Measured', marker=None)
    sp.set_title('Dipole coasting beam %s$\cdot10^9$' % coast_str)

    for sey_ctr, sey in enumerate(sey_vect):

        try:
            dip_contribution_per_meter, ob, t_bun = get_simulation_ob('ArcDipReal', sey, coast_str)
            dip_contribution_per_hc = dip_contribution_per_meter * l_dip
            sim_loss_per_hc = dip_contribution_per_hc + quad_contribution_per_hc + drift_contribution_per_hc

            if sey_ctr == 0:
                label = coast_str + ' e9 coasting'
            else:
                label = None
            color_curr = ms.colorprog(sey_ctr, N_sims)

            sp_el.semilogy(ob.t/25e-9, ob.Nel_timep, color=color_curr, label=label, ls=coast_linestyle_dict[coast_str])

            if coast_ctr == 0:
                label = sey
            else:
                label = None

            ms.sciy()
            sp.plot(t_bun[:-1]/25e-9, sim_loss_per_hc, '.-', color=color_curr, label=label, marker=None)

        except IOError as err:
            print('Got:', err, sey, coast_str)

    sp.fill_between(t_bun[:-1]/25e-9, t_bun_zeros, drift_contribution_per_hc, alpha=0.4, color='red', label='Drift 0.5 $\cdot10^9$ coasting')
    sp.fill_between(t_bun[:-1]/25e-9, drift_contribution_per_hc, drift_contribution_per_hc+quad_contribution_per_hc, alpha=0.4, color='blue', label='Quad 0.5 $\cdot10^9$ coasting')

    if coast_ctr == 0:
        sp.legend(bbox_to_anchor=(1, 1.02),  loc='upper left', title='Dip SEY')
    elif coast_ctr == 2:
        sp.set_xlabel('25 ns slot')

sp_el.legend(bbox_to_anchor=(1, 1.02),  loc='upper left')

###
fig_all_nr = len(coast_strs)
for fig_nr in xrange(len(coast_strs)+1):
    min_bunch_nr = 3000
    fig = plt.figure()
    window_title_str = 'Simulated bunch by bunch power losses for different devices %i.' % fig_nr
    fig.canvas.set_window_title(window_title_str)
    if fig_nr == fig_all_nr:
        suptitle_str = 'Simulated bunch power losses'
    else:
        suptitle_str = 'Simulated bunch power losses for %s e9 coasting beam' % coast_strs[fig_nr]
    plt.suptitle(suptitle_str,fontsize=25)

    sp = None
    for dev_ctr, device in enumerate(devices):
        sp_ctr = dev_ctr +1
        sp = plt.subplot(3,1,sp_ctr, sharex=sp)
        sp.set_title(device)
        ms.sciy()
        sp.set_ylabel('Power loss [W/m]')
        if sp_ctr == 3:
            sp.set_xlabel('25 ns slot')

        for coast_ctr, coast_str in enumerate(coast_strs):
            if fig_nr != fig_all_nr and fig_nr != coast_ctr:
                continue
            for sey_ctr, sey in enumerate(sey_vect):
                try:
                    contribution_per_meter, ob, t_bun = get_simulation_ob(device, sey, coast_str)

                    color_curr = ms.colorprog(sey_ctr, N_sims)
                    if sp_ctr == 1 and coast_ctr == 0 or coast_ctr == fig_nr:
                        label = sey
                    elif sp_ctr == 2 and sey_ctr == 0 and fig_nr == fig_all_nr:
                        label = coast_str
                    else:
                        label = None

                    if fig_nr == fig_all_nr:
                        ls = coast_linestyle_dict[coast_str]
                    else:
                        ls = '-'

                    sp.plot(t_bun[min_bunch_nr:-1]/25e-9, contribution_per_meter[min_bunch_nr:], '.-', color=color_curr, label=label, ls=ls, marker=None)

                except IOError as err:
                    print('Got:', err, device, coast_str, sey)

        if sp_ctr == 1:
            sp.legend(bbox_to_anchor=(1, 1.02),  loc='upper left', title='SEY')
        elif sp_ctr == 2 and fig_nr == len(coast_strs):
            sp.legend(bbox_to_anchor=(1, 1.02),  loc='upper left', title='$10^9$ coasting')

plt.show()
