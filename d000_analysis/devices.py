import numpy as np
import matplotlib.pyplot as plt
import itertools

from pyecloud_device import pyecloud_device

def main(device_list,device_labels_dict, sey_list, coast_strs, dict_keys, hl_pyecloud,
        scenarios_labels_dict, length, coast_linestyle_dict):

    one_list = np.ones_like(sey_list)
    pyecloud_device_easy = lambda device, coast_str: pyecloud_device(device, coast_str, device_list, coast_strs, hl_pyecloud)

    fig = plt.figure()
    title_str = 'Heat loads for different devices and scenarios, per m and scaled'
    fig.canvas.set_window_title(title_str)
    plt.suptitle(title_str,fontsize=22)

    for dev_ctr, device in enumerate(device_list):
        sp = plt.subplot(2,2,dev_ctr+1)
        title = device_labels_dict[device]
        sp.set_title(title,fontsize=20)

        sp.set_xlabel('SEY Parameter')
        sp.set_ylabel('Heat load per m [W]')
        sp2 = sp.twinx()
        sp2.set_ylabel('Heat load per half cell [W]')
        sp2.grid('off')

        colors = itertools.cycle(plt.rcParams['axes.prop_cycle'])
        for sce_ctr,sce in enumerate(dict_keys):
            color = colors.next()[u'color']
            for coast_ctr, coast_str in enumerate(coast_strs):
                data = pyecloud_device_easy(device,coast_str)
                if coast_ctr == 0 and dev_ctr ==1:
                    label = scenarios_labels_dict[sce]
                elif dev_ctr == 2 and sce_ctr == 0:
                    label = coast_str + ' e9 coasting'
                else:
                    label = None
                ls = coast_linestyle_dict[coast_str]
                sp.plot(sey_list,data[sce_ctr,:],label=label,color=color, ls=ls)

        if dev_ctr == 1 or dev_ctr == 2:
            sp.legend(bbox_to_anchor=(1.1, 1),loc='upper left',fontsize=18)

        axes_factor = length[device]
        unscaled_min, unscaled_max =  sp.get_ylim()
        sp2.set_ylim(axes_factor*unscaled_min,axes_factor*unscaled_max)
