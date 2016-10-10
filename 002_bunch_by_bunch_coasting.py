import sys
sys.path.append('../backup_lhcscrub_python/LHCMeasurementTools')
import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio

import myfilemanager as mlo
import mystyle as ms
from LHC_Heatloads import magnet_length

T_rev = 88.9e-6
qe = 1.60217657e-19

main_folder = './all_data'
beam_snapshot_folder = './beam_snapshots'

machine_name = 'LHC'
device_name = 'ArcDipReal'
beam_name = '6500GeV'
coast_str = '0.5'

coast_strs = ['1.0', '0.5', '0.0']
coast_linestyle_dict = {\
        '1.0': '-',
        '0.5': '-.',
        '0.0': ':'
        }

list_beam_snapshots = [\
'Fill4177_cut1.680h_450GeV_for_triplets_B2.mat']

beam_snapshot = 'Fill5219_cut0.920h_450GeV_for_triplets_B1.mat'
beam_snapshot = 'Fill5219_cut0.920h_450GeV_for_triplets_B1.mat'
beam_snapshot = 'Fill5219_cut1.800h_6500GeV_for_triplets_B1.mat'

ob_snapshot = mlo.myloadmat_to_obj(beam_snapshot_folder+'/'+beam_snapshot)
l_hc = magnet_length['AVG_ARC']
meas_loss_per_meter = ob_snapshot.bunch_power_loss/23./2./8./l_hc

sey_vect = np.arange(1.10,1.501,.05)

if 'B1' in beam_snapshot:
	colorbeam = 'b'
elif 'B2' in beam_snapshot:
	colorbeam = 'r'
else:
	raise ValueError('Beam type (B1 or B2) could not be infered from the name of the snapshot')

sey_min_rmserr = None
min_rms_err = np.inf

N_sims = len(sey_vect)
hl = []

plt.close('all')
ms.mystyle(15)
plt.figure
sp0 = plt.subplot(3,1,1)
sp1 = plt.subplot(3,1,2, sharex=sp0)

# print simulation data
for coast_str in coast_strs:
    for ii in xrange(len(sey_vect)):

            sey = sey_vect[ii]
            print beam_snapshot, device_name, sey

            current_sim_ident= '%s_%s_%s_%s_sey%.2f_coast%s'%(beam_snapshot.split('.mat')[0],machine_name, device_name,
                    beam_name, sey,coast_str)
            print(current_sim_ident)
            try:
                    #ob = mlo.myloadmat_to_obj(main_folder+'/'+current_sim_ident+'/Pyecltest.mat')
                    ob = mlo.myloadmat_to_obj(main_folder + '/' + current_sim_ident+'/Pyecltest.mat')

                    t_bun = np.arange(0.,np.max(ob.t),  ob.b_spac)
                    L_imp_t = np.cumsum(ob.En_imp_eV_time-ob.En_emit_eV_time); #in eV
                    L_imp = np.interp(t_bun, ob.t, L_imp_t) #in eV
                    Ek = np.interp(t_bun, ob.t, ob.En_kin_eV_time);
                    sim_loss_per_meter = (np.diff(L_imp) + np.diff(Ek))*qe/T_rev; #watt/m
                    color_curr = ms.colorprog(ii, N_sims)

                    if ii == 0:
                        label = coast_str + ' e9 coasting'
                    else:
                        label = None
                    sp1.semilogy(ob.t/25e-9, ob.Nel_timep, color=color_curr, label=label, ls=coast_linestyle_dict[coast_str])

                    if coast_str == coast_strs[0]:
                        label = sey_vect[ii]
                    else:
                        label = None

                    sp2 = plt.subplot(3,1,3, sharex=sp1)
                    ms.sciy()
                    sp2.plot(t_bun[:-1]/25e-9, sim_loss_per_meter, '.-', color=color_curr, label=label, ls=coast_linestyle_dict[coast_str])

                    rmserr = np.sqrt(np.sum((sim_loss_per_meter - meas_loss_per_meter[:len(sim_loss_per_meter)])**2))
                    if rmserr < min_rms_err:
                            sey_min_rmserr = sey
                            min_rms_err = rmserr

                    hl.append(np.sum(ob.energ_eV_impact_hist)*qe/T_rev)

            except IOError as err:
                            print 'Got:', err
                            hl.append(0.)

sp0.semilogy(ob_snapshot.ppb_vect, color=colorbeam,label='Measured')
for coast_str in coast_strs:
    coast_arr = np.ones_like(ob_snapshot.ppb_vect)*1e9*float(coast_str)
    label = coast_str + 'e9 coasting'
    ls = coast_linestyle_dict[coast_str]
    sp0.semilogy(coast_arr, color=colorbeam, label=label, ls=ls)

sp0.legend(bbox_to_anchor=(1, 1.02), loc='upper left')


#sp0.semilogy(ob_snapshot.ppb_vect)
sp0.set_ylabel('Bunch intensity [p$^+$]')
sp0.set_xlim(0,3500)
sp1.set_ylabel('Electrons [1/m]')

x_axis = np.arange(3564)
# sp2.plot(x_axis, meas_loss_per_meter, '.-', color='k')
sp2.plot(meas_loss_per_meter, '.-', color='k', label='Measured')
sp2.set_ylabel('Power loss [W/m]')
sp2.set_xlabel('25 ns slot')

sp1.legend(bbox_to_anchor=(1, 1.02),  loc='upper left', fontsize='medium')
sp2.legend(bbox_to_anchor=(1, 1.02),  loc='upper left', fontsize='medium')
plt.suptitle(beam_snapshot.split('.mat')[0]+'\nsey min rmserr %.2f'%sey_min_rmserr)

#fig100 = plt.figure(100)
#plt.plot(sey_vect, np.array(hl)*53.)

plt.show()
