import sys
sys.path.append('../backup_lhcscrub_python/LHCMeasurementTools')
import pylab as pl
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
coast_str = '0.0'

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

pl.close('all')
ms.mystyle(15)
pl.figure(1, figsize=(16,14))
sp0 = pl.subplot(3,1,1)
sp1 = pl.subplot(3,1,2, sharex=sp0)
for ii in xrange(len(sey_vect)):

	sey = sey_vect[ii]


	print beam_snapshot, device_name, sey
	
	current_sim_ident= '%s_%s_%s_%s_sey%.2f_coast%s'%(beam_snapshot.split('.mat')[0],machine_name, device_name, 
			beam_name, sey,coast_str)
        print(current_sim_ident)
	try:
		#ob = mlo.myloadmat_to_obj(main_folder+'/'+current_sim_ident+'/Pyecltest.mat')
		ob = mlo.myloadmat_to_obj('./all_data/' + current_sim_ident+'/Pyecltest.mat')
	

		t_bun = np.arange(0.,np.max(ob.t),  ob.b_spac)
		L_imp_t = np.cumsum(ob.En_imp_eV_time-ob.En_emit_eV_time); #in eV
		L_imp = np.interp(t_bun, ob.t, L_imp_t) #in eV
		Ek = np.interp(t_bun, ob.t, ob.En_kin_eV_time);
			
		sim_loss_per_meter = (np.diff(L_imp) + np.diff(Ek))*qe/T_rev; #watt/m

		# sim_loss_mask_beam = np.float_(sim_loss_per_meter != 0)
		# sim_loss_diff = np.diff(sim_loss_mask_beam)
		# sim_batch1_end_i = np.where(meas_loss_diff == -1)[0][1]
		# sim_batch1_start_i = np.where(t_bun == (t_bun[sim_batch1_end_i] - 25e-9*meas_train_len))[0][0]
		# print sim_batch1_start_i, sim_batch1_end_i

		color_curr = ms.colorprog(ii, N_sims)
		# sp1.plot(ob.t/25e-9, ob.Nel_timep, color=color_curr, label=sey_vect[ii])
		sp1.semilogy(ob.t/25e-9, ob.Nel_timep, color=color_curr, label=sey_vect[ii])

		sp2 = pl.subplot(3,1,3, sharex=sp1)
		ms.sciy()
		sp2.plot(t_bun[:-1]/25e-9, sim_loss_per_meter, '.-', color=color_curr, label=sey_vect[ii])
		# sp2.semilogy(t_bun[:-1]/25e-9, sim_loss_per_meter, '.-', color=color_curr, label=sey_vect[ii])

		rmserr = np.sqrt(np.sum((sim_loss_per_meter - meas_loss_per_meter[:len(sim_loss_per_meter)])**2))
		if rmserr < min_rms_err:
			sey_min_rmserr = sey
			min_rms_err = rmserr

		hl.append(np.sum(ob.energ_eV_impact_hist)*qe/T_rev)

	except IOError as err:
			print 'Got:', err
			hl.append(0.)

sp0.plot(ob_snapshot.ppb_vect, color=colorbeam)
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
pl.suptitle(beam_snapshot.split('.mat')[0]+'\nsey min rmserr %.2f'%sey_min_rmserr)

#fig100 = pl.figure(100)
#pl.plot(sey_vect, np.array(hl)*53.)

pl.show()		
		
		
