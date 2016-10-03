import numpy as np
import matplotlib.pyplot as plt
from pyecloud_device import pyecloud_device


def main(device_list,device_labels_dict, sey_list, coast_strs, dict_keys, hl_pm_measured, hl_pyecloud, scenarios_labels_dict, length):

    one_list = np.ones_like(sey_list)
    pyecloud_device_easy = lambda device, coast_str: pyecloud_device(device, coast_str, device_list, coast_strs, hl_pyecloud)

    fig = plt.figure()
    title_str = 'Heat loads for different devices and scenarios, per m and scaled'
    fig.canvas.set_window_title(title_str)
    plt.suptitle(title_str,fontsize=22)

    for dev_ctr, device in enumerate(device_list):
        sp = plt.subplot(len(device_list),1,dev_ctr+1)
        title = device_labels_dict[device]
        sp.set_title(title,fontsize=20)
        if dev_ctr == len(device_list)-1:
            sp.set_xlabel('SEY Parameter',fontsize=18)
        sp.set_ylabel('Heat load per m [W]',fontsize=18)
        sp2 = sp.twinx()
        sp2.set_ylabel('Heat load per half cell [W]',fontsize=18)
        sp2.grid('off')
        if device == 'ArcDipReal':
            #sp2.plot(sey_list,np.min(hl_pm_measured)*one_list,label='Min measured')
            #sp2.plot(sey_list,np.max(hl_pm_measured)*one_list,label='Max measured')
            sp2.legend(bbox_to_anchor=(1.1, 1),loc='upper left',fontsize=18)

        for coast_ctr, coast_str in enumerate(coast_strs):
            data = pyecloud_device_easy(device,coast_str)
            for sce_ctr,sce in enumerate(dict_keys):
                label = scenarios_labels_dict[sce] + ' ' + coast_str + 'e9 coasting'
                sp.plot(sey_list,data[sce_ctr,:],label=label)

        if dev_ctr == 1:
            sp.legend(bbox_to_anchor=(1.1, 1),loc='upper left',fontsize=18)
        axes_factor = length[device]
        unscaled_min, unscaled_max =  sp.get_ylim()
        sp2.set_ylim(axes_factor*unscaled_min,axes_factor*unscaled_max)

    plt.subplots_adjust(right=0.75, wspace=0.25)



