import sys
import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
import argparse

import LHCMeasurementTools.myfilemanager as mlo
import LHCMeasurementTools.mystyle as ms
from LHCMeasurementTools.LHC_Heatloads import magnet_length

from RcParams import init_pyplot
init_pyplot()

parser = argparse.ArgumentParser(description='Show bunch by bunch power losses from PyECLOUD simulations and measurements.')
parser.add_argument('q', help='Quadrupole SEY', metavar='Quad SEY', type=float)
parser.add_argument('d', help='Drift SEY', metavar='Drift SEY', type=float)
parser.add_argument('beam', help='B1 | B2', type=str, metavar='BEAM')
args = parser.parse_args()

if args.beam != 'B1' and args.beam != 'B2':
    raise ValueError('Incorrect specification of beam!')

assumed_quad_sey = args.q
assumed_drift_sey = args.d

T_rev = 88.9e-6
qe = 1.60217657e-19

main_folder = './all_data'
beam_snapshot_folder = './beam_snapshots'

machine_name = 'LHC'
devices = ['Drift', 'ArcDipReal', 'ArcQuadReal']
device_name = 'ArcDipReal'
beam_name = '6500GeV'

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

#beam_snapshot = 'Fill5219_cut0.920h_450GeV_for_triplets_B1.mat'
beam_snapshot = 'Fill5219_cut1.800h_6500GeV_for_triplets_%s.mat' % args.beam

ob_snapshot = mlo.myloadmat_to_obj(beam_snapshot_folder+'/'+beam_snapshot)
meas_loss_per_meter = ob_snapshot.bunch_power_loss/23./2./8./l_hc
meas_loss_per_hc = meas_loss_per_meter * l_hc

sey_vect = np.arange(1.10,1.501,.05)

if 'B1' in beam_snapshot:
    colorbeam = 'b'
elif 'B2' in beam_snapshot:
    colorbeam = 'r'
else:
    raise ValueError('Beam type (B1 or B2) could not be infered from the name of the snapshot')

N_sims = len(sey_vect)

def get_simulation_ob(device_name, sey, coast_str='0.5'):

    sim_ident = '%s_%s_%s_%s_sey%.2f_coast%s' % (beam_snapshot.split('.mat')[0], machine_name, device_name, beam_name, sey, coast_str)
    ob = mlo.myloadmat_to_obj(main_folder + '/' + sim_ident+'/Pyecltest.mat')
    # from Gianni
    t_bun = np.arange(0.,np.max(ob.t),  ob.b_spac)
    L_imp_t = np.cumsum(ob.En_imp_eV_time-ob.En_emit_eV_time); #in eV
    L_imp = np.interp(t_bun, ob.t, L_imp_t) #in eV
    Ek = np.interp(t_bun, ob.t, ob.En_kin_eV_time);
    sim_loss_per_meter = (np.diff(L_imp) + np.diff(Ek))*qe/T_rev; #watt/m

    return sim_loss_per_meter, ob, t_bun

quad_contribution_per_meter, quad_ob,t_bun = get_simulation_ob('ArcQuadReal', assumed_quad_sey)
drift_contribution_per_meter, drift_ob,t_bun = get_simulation_ob('Drift', assumed_drift_sey)

plt.close('all')
fig = plt.figure()
title_str = 'Comparison of measured to simulated bunch by bunch power losses.'
fig.canvas.set_window_title(title_str)
title_str += '\nAssumed Quad/Drift SEY: %.2f/%.2f' % (assumed_quad_sey,assumed_drift_sey)
plt.suptitle(title_str,fontsize=25)
sp0 = plt.subplot(3,1,1)
sp1 = plt.subplot(3,1,2, sharex=sp0)

# plot simulation data
for coast_ctr, coast_str in enumerate(coast_strs):
    for sey_ctr, sey in enumerate(sey_vect):
        #print beam_snapshot, device_name, sey

        try:
            dip_contribution_per_meter, ob, t_bun = get_simulation_ob('ArcDipReal', sey, coast_str)
            sim_loss_per_hc = dip_contribution_per_meter * l_dip + quad_contribution_per_meter * l_quad + drift_contribution_per_meter * l_drift

            if sey_ctr == 0:
                label = coast_str + ' e9 coasting'
            else:
                label = None
            color_curr = ms.colorprog(sey_ctr, N_sims)

            sp1.semilogy(ob.t/25e-9, ob.Nel_timep, color=color_curr, label=label, ls=coast_linestyle_dict[coast_str])

            if coast_ctr == 0:
                label = sey
            else:
                label = None

            sp2 = plt.subplot(3,1,3, sharex=sp1)
            ms.sciy()
            sp2.plot(t_bun[:-1]/25e-9, sim_loss_per_hc, '.-', color=color_curr, label=label, ls=coast_linestyle_dict[coast_str])

        except IOError as err:
            print('Got:', err)

sp0.plot(ob_snapshot.ppb_vect, color=colorbeam,label='Measured')
sp0.set_ylabel('Bunch intensity [p$^+$]')
sp0.set_xlim(0,3500)

sp1.set_ylabel('Electrons [1/m]')

sp2.plot(meas_loss_per_hc, '.-', color='k', label='Measured')
sp2.set_ylabel('Power loss [W/hc]')
sp2.set_xlabel('25 ns slot')

sp1.legend(bbox_to_anchor=(1, 1.02),  loc='upper left')
sp2.legend(bbox_to_anchor=(1, 1.02),  loc='upper left')


# Figure for devices only

fig_all_nr = len(coast_strs)
for fig_nr in xrange(len(coast_strs)+1):
    min_bunch_nr = 3000
    fig = plt.figure()
    window_title_str = 'Simulated bunch by bunch power losses for different devices %i.' % fig_nr
    fig.canvas.set_window_title(title_str)
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
                    print('Got:', err)

        if sp_ctr == 1:
            sp.legend(bbox_to_anchor=(1, 1.02),  loc='upper left', title='SEY')
        elif sp_ctr == 2 and fig_nr == len(coast_strs):
            sp.legend(bbox_to_anchor=(1, 1.02),  loc='upper left', title='$10^9$ coasting')

plt.show()
