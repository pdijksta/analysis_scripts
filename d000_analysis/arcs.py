import numpy as np
import matplotlib.pyplot as plt
import itertools

def main(hl_pyecloud, hl_measured, length, arc_uncertainty, scenarios_labels_dict, arcs, sey_list, coast_strs, dict_keys, devices, coast_linestyle_dict):
    one_list = np.ones_like(sey_list)


    data = np.zeros((len(dict_keys),len(coast_strs),len(sey_list)))
    for key_ctr in xrange(len(dict_keys)):
        for coast_ctr in xrange(len(coast_strs)):
            for device_ctr, device in enumerate(devices):
                data[key_ctr,coast_ctr,:] += hl_pyecloud[key_ctr,device_ctr,coast_ctr,:] * length[device]

#    sp = None
#    fig_ctr = 0
#    for key_ctr,key in enumerate(dict_keys):
#        if key_ctr % 4 == 0:
#            fig = plt.figure()
#            fig_ctr += 1
#            title_str = 'Half cell heat loads %i' % fig_ctr
#            fig.canvas.set_window_title(title_str)
#            plt.suptitle(title_str,fontsize=24)
#
#        sp = plt.subplot(2,2,(key_ctr%4)+1,sharex=sp)
#        sp.set_xlabel('SEY Parameter',fontsize=18)
#        sp.set_ylabel('Heat load [W]',fontsize=18)
#
#        uncertainty = np.mean(arc_uncertainty[key_ctr,:])
#        uncertainty_str = 'Mean heat load uncertainty: %.1f W' % uncertainty
#        sp.set_title(scenarios_labels_dict[key]+' - '+uncertainty_str, fontsize=20)
#
#        for arc_ctr, arc in enumerate(arcs):
#            label = arc
#            sp.plot(sey_list, hl_measured[key_ctr,arc_ctr]*one_list, '--', label=label)
#        
#        color='0.1'
#        for coast_ctr, coast_str in enumerate(coast_strs):
#            label = coast_str + 'e9 coasting beam'
#            sp.plot(sey_list, data[key_ctr,coast_ctr,:], ls=coast_linestyle_dict[coast_str], color=color, label=label)
#
#        if key_ctr%4  == 1:
#            sp.legend(bbox_to_anchor=(1.1, 1))

    # plot for every single arc
    
    fig_ctr = 0
    sp = None
    for arc_ctr, arc in enumerate(arcs):
        colors = itertools.cycle(plt.rcParams['axes.prop_cycle'])

        if arc_ctr % 4 == 0:
            fig = plt.figure()
            fig_ctr += 1
            title_str = 'Half cell heat loads %i' % fig_ctr
            fig.canvas.set_window_title(title_str)
            plt.suptitle(title_str,fontsize=24)

        sp = plt.subplot(2,2,(arc_ctr%4)+1, sharex = sp)
        sp.set_xlabel('SEY Parameter',fontsize=18)
        sp.set_ylabel('Heat load [W]',fontsize=18)
        sp.set_title('Mean heat load uncertainty: %.1f W' % np.mean(arc_uncertainty[:,arc_ctr]))
        
        for key_ctr, key in enumerate(dict_keys):
            color = colors.next()[u'color']
            sp.plot(sey_list, hl_measured[key_ctr,arc_ctr]*one_list, '--', color=color)
            for coast_ctr, coast_str in enumerate(coast_strs):
                ls = coast_linestyle_dict[coast_str]
                label = None
                if ls == '-':
                    label = key
                sp.plot(sey_list, data[key_ctr, coast_ctr,:], ls=ls, color=color, label=label)

        if arc_ctr % 4 == 1:
            sp.legend(bbox_to_anchor=(1.1, 1))
