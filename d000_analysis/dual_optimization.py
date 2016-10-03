# Interpolate data for dual optim
import numpy as np
import matplotlib.pyplot as plt
# Function for device
def pyecloud_device(hl_pyeclou, device, coast_str):
    if device not in device_list or coast_str not in coast_str:
        raise ValueError('Wrong device name or coast string in pyecloud_device!')

    dev_ctr = device_list.index(device)
    coast_ctr = coast_strs.index(coast_str)

    hl_device = hl_pyecloud[:,device_ctr,coast_ctr,:]

    return hl_device


def main():
    dip_begin = 1.15
    dip_end = 1.51
    step = 0.01
    dip_sey_list = np.arange(dip_begin,dip_end+.1*step,step)

    dip_data = (pyecloud_device('ArcDipReal','0.5') + pyecloud_device('ArcDipReal','1.0'))/2*length['ArcDipReal']
    quad_raw = pyecloud_quad()
    quad_data = np.mean(quad_raw,axis=2)*length['ArcQuadReal']

    data = np.zeros(shape=(len(dict_keys),len(arcs),len(dip_sey_list),2))
    for key_ctr in xrange(len(dict_keys)):
        for arc_ctr in xrange(len(arcs)):
            measured = hl_measured[key_ctr,arc_ctr]

            for dip_ctr, dip_sey in enumerate(dip_sey_list):
                dip_hl = np.interp(dip_sey,sey_list,dip_data[key_ctr,:])
                quad_hl_list = quad_data[key_ctr,:]

                data[key_ctr,arc_ctr,dip_ctr,0] = dip_sey
                if dip_hl + np.min(quad_hl_list) > measured or dip_hl + np.max(quad_hl_list) < measured:
                    #print('continue for %.2f' % dip_sey)
                    continue
                quad_hl = measured - dip_hl
                data[key_ctr,arc_ctr,dip_ctr,1] = np.interp(quad_hl,quad_data[key_ctr,:],sey_list)

    fig_ctr = 0
    for arc_ctr, arc in enumerate(arcs):
        if arc_ctr%4 == 0:
            fig = plt.figure()
            fig_ctr += 1
            title_str = 'Valid pairs of dip and quad SEY %i' % fig_ctr
            plt.suptitle(title_str,fontsize=22)
            fig.canvas.set_window_title(title_str)

        sp = plt.subplot(2,2,arc_ctr%4+1)

        # pyecloud data, measured only for labels/title
        for key_ctr, key in enumerate(dict_keys[:3]):
            hl = hl_measured[key_ctr,arc_ctr]
            label = '%s %.1f W' % (scenarios_labels_dict[key],hl)
            possible_xdata = data[key_ctr,arc_ctr,:,0]
            possible_ydata = data[key_ctr,arc_ctr,:,1]
            xdata, ydata = [], []
            for ctr, yy in enumerate(possible_ydata):
                if yy != 0:
                    xdata.append(possible_xdata[ctr])
                    ydata.append(yy)

            plt.plot(xdata, ydata, label=label)

        # Add diagonal lines
        ylim = sp.get_ylim()
        xlim = sp.get_xlim()
        diag_left = max(ylim[0], xlim[0])
        diag_right = min(ylim[1],xlim[1])
        sp.plot([diag_left, diag_right], [diag_left,diag_right], '--', color='black', label='diagonal')

        sp.set_title('Arc %s' % arc, fontsize=20)
        sp.set_xlabel('Dipole SEY', fontsize=18)
        sp.set_ylabel('Quad SEY', fontsize=18)
        sp.legend(loc='upper right')
