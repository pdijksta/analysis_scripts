import numpy as np
import matplotlib.pyplot as plt
from pyecloud_device import pyecloud_device

def main(devices, coast_strs, hl_pyecloud, hl_pm_measured_quads, dict_keys, quad_uncertainty, quads, sey_list, scenarios_labels_dict):

    one_list = np.ones_like(sey_list)
    pyecloud_device_easy = lambda device, coast_str: pyecloud_device(device, coast_str, devices, coast_strs, hl_pyecloud)

    fig = plt.figure()
    title_str = 'Fill by Fill heat loads - Quadrupoles'
    fig.canvas.set_window_title(title_str)
    plt.suptitle(title_str,fontsize=24)

    for key_ctr,key in enumerate(dict_keys):
        if key_ctr == 0:
            sp = plt.subplot(2,2,key_ctr+1)
        else:
            sp = plt.subplot(2,2,key_ctr+1,sharex=sp)
        sp.set_xlabel('SEY Parameter', fontsize=18)
        sp.set_ylabel('Heat load per m [W]', fontsize=18)

        uncertainty = np.mean(quad_uncertainty[key_ctr,:])
        uncertainty_str = 'Mean heat load uncertainty: %.1f W' % uncertainty
        sp.set_title(scenarios_labels_dict[key]+' - '+uncertainty_str, fontsize=20)

        # measured data
        for quad_ctr, label in enumerate(quads):
            # Maybe skip 15 quads as the data quality seems to be bad unfortunately
            #if re_quad_15.match(label):
            #    continue
            sp.plot(sey_list, hl_pm_measured_quads[key_ctr,quad_ctr]*one_list, '--', label=label)

        # simulation data
        for coast_ctr, coast_str in enumerate(coast_strs):
            label = coast_str + 'e9 coasting'
            data = pyecloud_device_easy('ArcQuadReal',coast_str)
            sp.plot(sey_list, data[key_ctr,:], label=label)

        if key_ctr == 3:
            sp.legend(bbox_to_anchor=(1.1, 1))


# Plot all scenarios for same quad


    plt_ctr = 0
    title_str = 'Heat loads for quadrupoles'
    for quad_ctr, quad in enumerate(quads):
        if plt_ctr % 4 == 0:
            plt.figure()
            plt.suptitle(title_str + ' %i' % (plt_ctr+1))
            fig.canvas.set_window_title(title_str)
        elif plt_ctr % 4 == 3:
            sp.legend(bbox_to_anchor=(1.1, 1))
        plt_ctr += 1
        sp = plt.subplot(2,2,plt_ctr%4+1)
        sp.set_xlabel('SEY Parameter')
        sp.set_ylabel('Heat load per m [W]')
        sp.set_title(quad)

        sp.plot(sey_list,hl_pm_measured_quads[key_ctr,quad_ctr]*one_list, '--')

        for coast_ctr, coast_str in enumerate(coast_strs):
            data = pyecloud_device_easy('ArcQuadReal',coast_str)
            for key_ctr, key in enumerate(dict_keys):
                label = scenarios_labels_dict[key] + ' ' + coast_str + 'e9'
                sp.plot(sey_list, data[key_ctr,:], label=label)

