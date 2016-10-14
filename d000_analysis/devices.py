import numpy as np
import matplotlib.pyplot as plt
import itertools

from pyecloud_device import pyecloud_device

intensity_list = ['0.7e11', '0.9e11', '1.1e11']
energy_list = ['450GeV', '6.5TeV']

intensity_list_float = [float(string) for string in intensity_list]


def main(devices,device_labels_dict, sey_list, coast_strs, dict_keys, hl_pyecloud,
        scenarios_labels_dict, length, coast_linestyle_dict, get_energy, get_intensity):

    one_list = np.ones_like(sey_list)
    pyecloud_device_easy = lambda device, coast_str: pyecloud_device(device, coast_str, devices, coast_strs, hl_pyecloud)

    title_str = 'Heat loads for different devices and scenarios, per m and scaled'

    ##
    fig_all_nr = 2
    for fig_nr in (1,2):
        fig = plt.figure()
        fig.canvas.set_window_title(title_str)
        plt.suptitle(title_str,fontsize=25)


        for dev_ctr, device in enumerate(devices):
            sp = plt.subplot(2,2,dev_ctr+1)
            title = device_labels_dict[device]
            sp.set_title(title,fontsize=20)

            sp.set_xlabel('SEY Parameter')
            sp.set_ylabel('Heat load per m [W]')
            sp2 = sp.twinx()
            sp2.set_ylabel('Heat load per half cell [W]')
            sp2.grid('off')

            colors = itertools.cycle(plt.rcParams['axes.prop_cycle'])
            for sce_ctr, sce in enumerate(dict_keys):
                color = colors.next()['color']
                for coast_ctr, coast_str in enumerate(coast_strs):
                    data = pyecloud_device_easy(device,coast_str)
                    if coast_ctr == 0 and dev_ctr ==1:
                        label = scenarios_labels_dict[sce]
                    elif dev_ctr == 2 and sce_ctr == 0 and fig_nr == fig_all_nr:
                        label = coast_str + ' e9 coasting'
                    else:
                        label = None
                    ls = coast_linestyle_dict[coast_str]

                    if fig_nr == fig_all_nr or coast_ctr == 0:
                        sp.plot(sey_list,data[sce_ctr,:],label=label,color=color, ls=ls)

            if dev_ctr == 1 or dev_ctr == 2 and fig_nr == fig_all_nr:
                sp.legend(bbox_to_anchor=(1.1, 1),loc='upper left')

            axes_factor = length[device]
            unscaled_min, unscaled_max =  sp.get_ylim()
            sp2.set_ylim(axes_factor*unscaled_min,axes_factor*unscaled_max)

    ##
    data = np.zeros(shape=(len(devices),len(energy_list), len(intensity_list_float), len(coast_strs), len(sey_list)))
    for key_ctr, key in enumerate(dict_keys):
        energy = get_energy(key)
        energy_ctr = energy_list.index(energy)
        intensity = get_intensity(key)
        intensity_ctr = intensity_list.index(intensity)
        for device_ctr, device in enumerate(devices):
            for coast_ctr, coast_str in enumerate(coast_strs):
                data[device_ctr,energy_ctr,intensity_ctr,coast_ctr,:] = hl_pyecloud[key_ctr,dev_ctr,coast_ctr,:]

#    for 
