# Interpolate data for dual optim
import numpy as np
import matplotlib.pyplot as plt
from pyecloud_device import pyecloud_device

from simulation_parameters import *

# Function for device
def main(const_device_short, const_sey_str, x_device_short, x_range_lower, x_range_higher, args_l=None, verbose=False):

    coast_str = '0.5'
    device_short_dict = {\
            'q': 'ArcQuadReal',
            'di': 'ArcDipReal',
            'dr': 'Drift'
            }

    # Reorder Arcs
    plot_arcs=['S81', 'S12', 'S23', 'S78', 'S56', 'S67', 'S45', 'S34']

    const_device = device_short_dict[const_device_short]
    x_device = device_short_dict[x_device_short]

    if const_device == x_device:
        raise ValueError('The same device was specified two times: %s %s!' % (const_device_short, x_device_short))

    for device in device_short_dict.values():
        if device not in [const_device, x_device]:
            y_device = device
            break
    else:
        raise ValueError('Could not find a y_device!')

    # Account for Low energy sims do not include drifts
    if y_device == 'Drift' or x_device == 'Drift':
        plot_dict_keys = []
        print('Removing low energy scenarios.')
        for key in dict_keys:
            if get_energy(key) != '450GeV':
                plot_dict_keys.append(key)
    else:
        plot_dict_keys = dict_keys

    for sey_ctr, sey in enumerate(sey_list):
        if round(sey,2) == float(const_sey_str):
            const_sey = sey
            const_sey_ctr = sey_ctr
            break
    else:
        raise ValueError('Could not find a matching sey for const_sey %s' % const_sey_str)


    pyecloud_device_easy = lambda device, coast_str: pyecloud_device(device, coast_str, devices, coast_strs, hl_pyecloud)

    x_begin = float(x_range_lower)
    x_end = float(x_range_higher)
    step = 0.005
    x_sey_list = np.arange(x_begin,x_end+.1*step,step)

    x_data = pyecloud_device_easy(x_device, coast_str) * length[x_device]
    y_data = pyecloud_device_easy(y_device,coast_str) * length[y_device]
    const_data = pyecloud_device_easy(const_device, coast_str) * length[const_device]

    data = np.zeros(shape=(len(dict_keys),len(arcs),len(x_sey_list),2))
    for key_ctr, key in enumerate(dict_keys):
        const_hl = const_data[key_ctr,const_sey_ctr]
        for arc_ctr, arc in enumerate(arcs):
            measured = hl_measured[key_ctr,arc_ctr]
            if verbose:
                print('%s %s %.1f' % (key, arc, measured))
            for x_ctr, x_sey in enumerate(x_sey_list):
                x_hl = np.interp(x_sey,sey_list,x_data[key_ctr,:])
                y_hl_list = y_data[key_ctr,:]

                data[key_ctr,arc_ctr,x_ctr,0] = x_sey
                if const_hl + np.min(y_hl_list) + x_hl > measured or x_hl + np.max(y_hl_list) + const_hl < measured:
                    if verbose:
                        print('continue for %s %s %.2f' % (key, arc, x_sey))
                    # else:
                    #    print('measured: %2f\t min simulated: %2f\t max simulated: %2f' % (measured, const_hl+x_hl+np.min))
                    continue
                y_hl = measured - x_hl - const_hl
                data[key_ctr,arc_ctr,x_ctr,1] = np.interp(y_hl,y_data[key_ctr,:],sey_list)

    fig_ctr = 0
    sp_ctr = 0
    for arc in plot_arcs:
        arc_ctr = arcs.index(arc)
        sp_ctr %= 4
        sp_ctr += 1
        if sp_ctr == 1:
            fig = plt.figure()
            fig_ctr += 1

            title_str = 'Valid pairs of %s and %s SEY %i. Average of two coasting intensities.' \
                    % (device_labels_dict[x_device], device_labels_dict[y_device], fig_ctr)
            fig.canvas.set_window_title(title_str)

            title_str += '\n %s SEY: %.2f.   Coasting beam: %s$\cdot 10^9$' % (device_labels_dict[const_device], const_sey, coast_str)
            plt.suptitle(title_str,fontsize=25)

        sp = plt.subplot(2,2,sp_ctr)

        # pyecloud data, measured only for labels/title
        for key_ctr, key in enumerate(dict_keys):
            if key not in plot_dict_keys:
                continue
            hl = hl_measured[key_ctr,arc_ctr]
            label = scenarios_labels_dict[key]
            possible_xdata = data[key_ctr,arc_ctr,:,0]
            possible_ydata = data[key_ctr,arc_ctr,:,1]
            xdata, ydata = [], []
            for ctr, yy in enumerate(possible_ydata):
                if yy != 0:
                    xdata.append(possible_xdata[ctr])
                    ydata.append(yy)

            sp.plot(xdata, ydata, label=label)

        sp.set_title('Arc %s' % arc, fontsize=20)
        sp.set_xlabel('%s SEY' % device_labels_dict[x_device])
        sp.set_ylabel('%s SEY' % device_labels_dict[y_device])

        # Prevent too ugly plots
        min_y, max_y = sp.get_ylim()
        min_y = min(min_y,1.1)
        max_y = max(max_y,1.2)
        sp.set_ylim(min_y,max_y)
        sp.set_xlim(x_begin,x_end)

        # Add vertical line for Quad SEY
        if args_l is not None:
            for xx_str in args_l:
                xx = float(xx_str)
                sp.axhline(xx, ls='--', color='orange')

        if sp_ctr == 2:
            sp.legend(bbox_to_anchor=(1.1, 1))
