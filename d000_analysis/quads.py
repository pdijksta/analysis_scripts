import numpy as np
import matplotlib.pyplot as plt
import itertools

from pyecloud_device import pyecloud_device

def main(devices, coast_strs, hl_pyecloud, hl_pm_measured_quads, dict_keys, quad_uncertainty,
        quads, sey_list, scenarios_labels_dict, coast_linestyle_dict):

    one_list = np.ones_like(sey_list)
    pyecloud_device_easy = lambda device, coast_str: pyecloud_device(device, coast_str, devices, coast_strs, hl_pyecloud)

    fig_ctr = 0
    for quad_ctr, quad in enumerate(quads):
        if quad_ctr % 4 == 0:
            fig=plt.figure()
            fig_ctr += 1
            title_str = 'Heat loads for quadrupoles' + ' %i' % fig_ctr
            plt.suptitle(title_str)
            fig.canvas.set_window_title(title_str)
        sp = plt.subplot(2,2,quad_ctr%4+1)
        sp.set_xlabel('SEY Parameter')
        sp.set_ylabel('Heat load per m [W]')
        sp.set_title(quad)

        colors = itertools.cycle(plt.rcParams['axes.prop_cycle'])
        
        inters_min = np.inf
        inters_max = -np.inf

        for key_ctr, key in enumerate(dict_keys):
            color = colors.next()[u'color']
            measured = hl_pm_measured_quads[key_ctr,quad_ctr]
            sp.plot(sey_list, measured*one_list, '--', color=color)

            for coast_ctr, coast_str in enumerate(coast_strs):

                data = pyecloud_device_easy('ArcQuadReal',coast_str)

                # get intersection point
                sey_int = np.interp(measured,data[key_ctr,:],sey_list)
                inters_min = min(inters_min, sey_int)
                inters_max = max(inters_max, sey_int)

                if coast_ctr == 0:
                    label = scenarios_labels_dict[key]
                else:
                    label = None
                ls = coast_linestyle_dict[coast_str]
                sp.plot(sey_list, data[key_ctr,:], label=label, color=color, ls=ls)

        # Make nicer plots
        y_lim = sp.get_ylim()
        x_lim = sp.get_xlim()
        plot_min = max(x_lim[0]+0.005, inters_min)
        plot_max = min(x_lim[1]-0.005, inters_max)
        plt.axvline(plot_min, y_lim[0], y_lim[1], ls='-', color='0.3', label='min/max SEY')
        plt.axvline(plot_max, y_lim[0], y_lim[1], ls='-', color='0.3')

        if quad_ctr % 4 == 3:
            sp.legend(bbox_to_anchor=(1.1, 1))
