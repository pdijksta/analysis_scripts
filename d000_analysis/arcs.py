import numpy as np
import matplotlib.pyplot as plt

def main(hl_pyecloud, hl_measured, length, arc_uncertainty, scenarios_labels_dict, arcs, sey_list, coast_strs, dict_keys, devices):
    one_list = np.ones_like(sey_list)

    fig = plt.figure()
    title_str = 'Half cell heat loads'
    fig.canvas.set_window_title(title_str)
    plt.suptitle(title_str,fontsize=24)
    plt.subplots_adjust(right=0.8, wspace=0.20)

    data = np.zeros((len(dict_keys),len(coast_strs),len(sey_list)))
    for key_ctr in xrange(len(dict_keys)):
        for coast_ctr in xrange(len(coast_strs)):
            for device_ctr, device in enumerate(devices):
                data[key_ctr,coast_ctr,:] += hl_pyecloud[key_ctr,device_ctr,coast_ctr,:] * length[device]

    sp = None
    for key_ctr,key in enumerate(dict_keys):
        sp = plt.subplot(2,2,key_ctr+1,sharex=sp)
        sp.set_xlabel('SEY Parameter',fontsize=18)
        sp.set_ylabel('Heat load [W]',fontsize=18)

        uncertainty = np.mean(arc_uncertainty[key_ctr,:])
        uncertainty_str = 'Mean heat load uncertainty: %.1f W' % uncertainty
        sp.set_title(scenarios_labels_dict[key]+'\n'+uncertainty_str, fontsize=20)

        for arc_ctr in xrange(len(arcs)):
            label = arcs[arc_ctr]
            sp.plot(sey_list, hl_measured[key_ctr,arc_ctr]*one_list, '--', label=label)

        for coast_ctr in xrange(len(coast_strs)):
            coast_str = coast_strs[coast_ctr]
            label = coast_str + 'e9 coasting beam'
            sp.plot(sey_list, data[key_ctr,coast_ctr,:], label=label)

        if key_ctr == 1:
            sp.legend(bbox_to_anchor=(1.1, 1),loc='upper left',fontsize=18)


