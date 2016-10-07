import numpy as np
import matplotlib.pyplot as plt
import itertools

# TODO: automate these 2 lists!
intensity_list = ['0.7e11', '0.9e11', '1.1e11']
intensity_list_float = [float(string) for string in intensity_list]
energy_list = ['450GeV', '6.5TeV']

def plot_keys(keys_list, name, uncertainty, hl_total, hl):
    for key_ctr, key in enumerate(keys_list):
        if arc_ctr%4 == 0:
            fig = plt.figure()
            title = 'Measured HL for %s %i' % (name, int(key_ctr/4)+1)
            fig.canvas.set_window_title(title)
            plt.suptitle(title)

        sp_nr = key_ctr%4 + 1
        sp = plt.subplot(2,2,sp_nr)
        sp.set_ylabel('Heat Load per m [W]')
        sp.set_xlabel('Bunch Intensity [p+]')
        sp.set_title(key)
        sp.set_xlim(0.6e11,1.2e11)

        colors = itertools.cycle(plt.rcParams['axes.prop_cycle'])

        for energy_ctr, energy in enumerate(energy_list):
            color = colors.next()[u'color']
            this_hl = hl_total[key_ctr,energy_ctr,:]
            this_uncertainty = uncertainty[key_ctr,energy_ctr,:]
            lower = this_hl-this_uncertainty
            higher = this_hl+this_uncertainty

            sp.plot(intensity_list_float,this_hl, marker='x', label=energy, color=color)
            sp.fill_between(intensity_list_float,lower, higher)#, color=color)
            plt.plot(intensity_list_float, model[energy_ctr,:], marker='x', label='Model', color=color, ls='--')

        if sp_nr == 2:
            sp.legend(bbox_to_anchor=(1.1, 1))

    # All arcs in 1 plot
    fig = plt.figure()
    title = 'Measured HL for all Arcs, e-cloud only'
    fig.canvas.set_window_title(title)
    plt.suptitle(title)

    for energy_ctr, energy in enumerate(energy_list):
        sp = plt.subplot(2,2,energy_ctr+1)
        sp.set_ylabel('Heat Load per m [W]')
        sp.set_xlabel('Bunch Intensity [p+]')
        sp.set_title(energy)
        sp.set_xlim(0.6e11,1.2e11)

        for key_ctr, key in enumerate(keys):
            sp.plot(intensity_list_float,hl[key_ctr,energy_ctr,:], marker='x', label=arc)

        if energy_ctr == 1:
            sp.legend(bbox_to_anchor=(1.1, 1))


def main(hl_pm_measured, hl_pm_measured_quads, dict_keys, arcs, quads, scenarios_labels_dict,
        get_intensity, get_energy, hl_pm_model_arcs, hl_pm_model_quads, arc_pm_uncertainty):

    hl = np.zeros(shape=(len(arcs),len(energy_list),len(intensity_list)))
    hl_total = np.zeros_like(hl)
    uncertainty = np.zeros_like(hl)
    model = np.zeros(shape=(len(energy_list),len(intensity_list)))

    for key_ctr, key in enumerate(dict_keys):
        energy = get_energy(key)
        energy_ctr = energy_list.index(energy)
        intensity = get_intensity(key)
        intensity_ctr = intensity_list.index(intensity)
        model[energy_ctr,intensity_ctr] = hl_pm_model_arcs[key_ctr]

        for arc_ctr,arc in enumerate(arcs):
            hl[arc_ctr,energy_ctr,intensity_ctr] = hl_pm_measured[key_ctr,arc_ctr]
            hl_total[arc_ctr,energy_ctr,intensity_ctr] = hl[arc_ctr,energy_ctr,intensity_ctr] + model[energy_ctr,intensity_ctr]
            uncertainty[arc_ctr,energy_ctr,intensity_ctr] = arc_pm_uncertainty[key_ctr,arc_ctr]


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

        colors = itertools.cycle(plt.rcParams['axes.prop_cycle'])

        for energy_ctr, energy in enumerate(energy_list):
            color = colors.next()[u'color']
            this_hl = hl_total[arc_ctr,energy_ctr,:]
            this_uncertainty = uncertainty[arc_ctr,energy_ctr,:]
            lower = this_hl-this_uncertainty
            higher = this_hl+this_uncertainty

            sp.plot(intensity_list_float,this_hl, marker='x', label=energy, color=color)
            sp.fill_between(intensity_list_float,lower, higher)#, color=color)
            plt.plot(intensity_list_float, model[energy_ctr,:], marker='x', label='Model', color=color, ls='--')

        if sp_nr == 2:
            sp.legend(bbox_to_anchor=(1.1, 1))

    # All arcs in 1 plot
    fig = plt.figure()
    title = 'Measured HL for all Arcs, e-cloud only'
    fig.canvas.set_window_title(title)
    plt.suptitle(title)

    for energy_ctr, energy in enumerate(energy_list):
        sp = plt.subplot(2,2,energy_ctr+1)
        sp.set_ylabel('Heat Load per m [W]')
        sp.set_xlabel('Bunch Intensity [p+]')
        sp.set_title(energy)
        sp.set_xlim(0.6e11,1.2e11)

        for arc_ctr, arc in enumerate(arcs):
            sp.plot(intensity_list_float,hl[arc_ctr,energy_ctr,:], marker='x', label=arc)

        if energy_ctr == 1:
            sp.legend(bbox_to_anchor=(1.1, 1))
