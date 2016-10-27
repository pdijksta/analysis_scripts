import sys

import numpy as np
import matplotlib.pyplot as plt

from simulation_parameters import *

def main(drift_sey, dip_sey, quad_sey):

    dev_sey_dict = {\
            'ArcDipReal': dip_sey,
            'ArcQuadReal': quad_sey,
            'Drift': drift_sey
            }
    dev_color_dict = {\
            'ArcDipReal': 'blue',
            'ArcQuadReal': 'red',
            'Drift': 'green'
            }

    data = np.zeros(shape=(len(devices), len(coast_strs), len(energy_list), len(intensity_list_float)))
    measured = np.zeros(shape=(len(arcs), len(energy_list), len(intensity_list_float)))
    for key_ctr, key in enumerate(dict_keys):
        energy = get_energy(key)
        energy_ctr = energy_list.index(energy)
        intensity = get_intensity(key)
        intensity_ctr = intensity_list.index(intensity)

        for arc_ctr, arc in enumerate(arcs):
            measured[arc_ctr, energy_ctr, intensity_ctr] = hl_measured[key_ctr,arc_ctr]

        for dev_ctr, device in enumerate(devices):
            for coast_ctr, coast_str in enumerate(coast_strs):
                raw = hl_pyecloud[key_ctr,dev_ctr,coast_ctr,:] * length[device]
                data[dev_ctr, coast_ctr, energy_ctr,intensity_ctr] = np.interp(dev_sey_dict[device],sey_list,raw)

    coast_ctr = 1
    coast_str = coast_strs[coast_ctr]
    width = 0.2
    xx = np.array(range(len(energy_list)))

    max_yy = -np.inf
    for arc_ctr, arc in enumerate(arcs):
        sp_ctr = arc_ctr % 4 + 1

        if sp_ctr ==1:
            fig = plt.figure()
            title = 'Simulated heat loads for SEY Drift %.2f Dip %.2f Quad %.2f' % (drift_sey, dip_sey, quad_sey)
            fig.canvas.set_window_title(title)
            plt.suptitle(title, fontsize=25)
        sp = plt.subplot(2,2,sp_ctr)
        sp.set_ylabel('Heat load [W/hc]')
        sp.set_title(arc)

        sp.set_xticks(xx+1.5*width)
        sp.set_xticklabels([str(fl) for fl in energy_list])
        for intensity_ctr, intensity in enumerate(intensity_list_float):
            # Measured
            for energy_ctr, energy in enumerate(energy_list):
                xx_measured = [energy_ctr+intensity_ctr*width, energy_ctr + (intensity_ctr+1)*width]
                yy_measured = [measured[arc_ctr,energy_ctr, intensity_ctr]]*2
                if energy_ctr == 0 and intensity_ctr == 0:
                    label = 'Measured'
                else:
                    label = None
                sp.plot(xx_measured, yy_measured, ls='--', color='black', label=label)

            # Simulated
            bottom = np.zeros_like(energy_list,float)
            for dev_ctr, device in enumerate(devices):
                height = data[dev_ctr,coast_ctr,:,intensity_ctr]

                color = dev_color_dict[device]
                if intensity_ctr == 0:
                    label = device_labels_dict[device]
                else:
                    label = None
                sp.bar(xx+width*intensity_ctr, height=height, width=width, bottom=bottom, color=color, label=label, alpha=0.5)
                bottom += height
            max_yy = max(max_yy, np.max(bottom))
        sp.set_ylim(sp.get_ylim()[0], max_yy+10)
        if sp_ctr == 2:
            sp.legend(bbox_to_anchor=(1.1, 1))
