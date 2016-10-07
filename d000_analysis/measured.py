import numpy as np
import matplotlib.pyplot as plt

def main(hl_pm_measured, hl_pm_measured_quads, dict_keys, arcs, quads, scenarios_labels_dict, get_intensity, get_energy):

    intensity_list = ['0.7e11', '0.9e11', '1.1e11']
    energy_list = ['450GeV', '6.5TeV']

    data = np.ones(shape=(len(arcs),len(energy_list),(len(intensity_list)))) * (-100)

    for arc_ctr,arc in enumerate(arcs):
        for key_ctr, key in enumerate(dict_keys):
            energy = get_energy(key)
            energy_ctr = energy_list.index(energy)
            intensity = get_intensity(key)
            intensity_ctr = intensity_list.index(intensity)
            data[arc_ctr,energy_ctr,intensity_ctr] = hl_pm_measured[key_ctr,arc_ctr]

    for arc_ctr in xrange(len(arcs)):
        for key_ctr, key in enumerate(dict_keys):
            energy = get_energy(key)

    # Single Arcs 
    for arc_ctr, arc in enumerate(arcs):
        if arc_ctr%4 == 0:
            fig = plt.figure()
            title = 'Measured HL for Arcs %i' % (int(arc_ctr/4)+1)
            fig.canvas.set_window_title(title)
            plt.suptitle(title)

        sp_nr = arc_ctr%4 + 1
        sp = plt.subplot(2,2,sp_nr)
        sp.set_ylabel('Heat Load per m [W]')
        sp.set_xlabel('Bunch Intensity [p+]')
        sp.set_title(arc)
        sp.set_xlim(0.6e11,1.2e11)

        for energy_ctr, energy in enumerate(energy_list):
            plt.plot(intensity_list, data[arc_ctr,energy_ctr,:], marker='x', label=energy)

        if sp_nr == 2:
            sp.legend(bbox_to_anchor=(1.1, 1))

    # All arcs in 1 plot
    fig = plt.figure()
    title = 'Measured HL for all Arcs'
    fig.canvas.set_window_title(title)
    plt.suptitle(title)

    for energy_ctr, energy in enumerate(energy_list):
        sp = plt.subplot(2,2,energy_ctr+1)
        sp.set_ylabel('Heat Load per m [W]')
        sp.set_xlabel('Bunch Intensity [p+]')
        sp.set_title(energy)
        sp.set_xlim(0.6e11,1.2e11)

        for arc_ctr, arc in enumerate(arcs):
            plt.plot(intensity_list,data[arc_ctr,energy_ctr,:], marker='x', label=arc)
        
        if energy_ctr == 1:
            sp.legend(bbox_to_anchor=(1.1, 1))
