# Interpolate data for dual optim
import numpy as np
import matplotlib.pyplot as plt
from pyecloud_device import pyecloud_device

# Function for device
def main(hl_pyecloud, device_list, coast_strs, scenarios_labels_dict, length, dict_keys, arcs,
        hl_measured, sey_list, args_l, arguments, device_labels_dict, verbose=False):

    coast_str = '0.5'
    device_short_dict = {\
            'q': 'ArcQuadReal',
            'di': 'ArcDipReal',
            'dr': 'Drift'
            }

    const_device_short, const_sey_str, x_device_short, x_range_lower, x_range_higher = arguments
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

    for sey_ctr, sey in enumerate(sey_list):
        if round(sey,2) == float(const_sey_str):
            const_sey = sey
            const_sey_ctr = sey_ctr
            break
    else:
        raise ValueError('Could not find a matching sey for const_sey %s' % const_sey_str)


    pyecloud_device_easy = lambda device, coast_str: pyecloud_device(device, coast_str, device_list, coast_strs, hl_pyecloud)

    x_begin = float(x_range_lower)
    x_end = float(x_range_higher)
    step = 0.005
    x_sey_list = np.arange(x_begin,x_end+.1*step,step)

    x_data = pyecloud_device_easy(x_device, coast_str) * length[x_device]
    y_data = pyecloud_device_easy(y_device,coast_str) * length[y_device]
    const_data = pyecloud_device_easy(const_device, coast_str) * length[const_device]

    data = np.zeros(shape=(len(dict_keys),len(arcs),len(x_sey_list),2))
    for key_ctr in xrange(len(dict_keys)):
        const_hl = const_data[key_ctr,const_sey_ctr]
        for arc_ctr in xrange(len(arcs)):
            measured = hl_measured[key_ctr,arc_ctr]
            for x_ctr, x_sey in enumerate(x_sey_list):
                x_hl = np.interp(x_sey,sey_list,x_data[key_ctr,:])
                y_hl_list = y_data[key_ctr,:]

                data[key_ctr,arc_ctr,x_ctr,0] = x_sey
                if const_hl + np.min(y_hl_list) > measured or x_hl + np.max(y_hl_list) + const_hl < measured:
                    if verbose:
                        print('continue for %.2f' % dip_sey)
                    continue
                y_hl = measured - x_hl - const_hl
                data[key_ctr,arc_ctr,x_ctr,1] = np.interp(y_hl,y_data[key_ctr,:],sey_list)

    fig_ctr = 0
    for arc_ctr, arc in enumerate(arcs):
        if arc_ctr%4 == 0:
            fig = plt.figure()
            fig_ctr += 1

            title_str = 'Valid pairs of %s and %s SEY %i. Average of two coasting intensities.' \
                    % (device_labels_dict[x_device], device_labels_dict[y_device], fig_ctr)
            fig.canvas.set_window_title(title_str)

            title_str += '\n %s SEY: %.2f.   Coasting beam: %s$\cdot 10^9$' % (device_labels_dict[const_device], const_sey, coast_str)
            plt.suptitle(title_str,fontsize=25)

        sp = plt.subplot(2,2,arc_ctr%4+1)

        # pyecloud data, measured only for labels/title
        for key_ctr, key in enumerate(dict_keys):
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

        sp.axhline(const_sey, ls='--', color='black', label=device_labels_dict[const_device])


        sp.set_title('Arc %s' % arc, fontsize=20)
        sp.set_xlabel('%s SEY' % device_labels_dict[x_device])
        sp.set_ylabel('%s SEY' % device_labels_dict[y_device])
        #sp.set_xlim(xlim)
        #sp.set_ylim(ylim)

        # Add vertical line for Quad SEY
        if args_l is not None:
            for xx_str in args_l:
                xx = float(xx_str)
                sp.axhline(xx, ls='--', color='orange')

        if arc_ctr % 4 == 3:
            sp.legend(bbox_to_anchor=(1.1, 1))
