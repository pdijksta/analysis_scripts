import numpy as np
import matplotlib.pyplot as plt
import itertools

from simulation_parameters import intensity_list, intensity_list_float, energy_list

class Handle_devs:
    def __init__(self, devs_list, hl_pm_model, hl_pm_measured, dev_pm_uncertainty, get_energy, get_intensity, dict_keys, name, len_arc_quad_dict, model_label):

        self.devs_list = devs_list
        self.hl_pm_model = hl_pm_model
        self.name = name
        self.hl_pm_measured = hl_pm_measured
        self.dev_pm_uncertainty = dev_pm_uncertainty
        self.get_energy = get_energy
        self.get_intensity = get_intensity
        self.dict_keys = dict_keys
        self.length_dict = len_arc_quad_dict
        self.model_label = model_label

        self._create_data_arrays()

        self._plot_devs()

    def _create_data_arrays(self):

        # init
        hl = np.zeros(shape=(len(self.devs_list),len(energy_list),len(intensity_list)))
        hl_total = np.zeros_like(hl)
        uncertainty = np.zeros_like(hl)
        model = np.zeros(shape=(len(energy_list),len(intensity_list)))

        # fill lists
        for key_ctr, key in enumerate(self.dict_keys):
            energy = self.get_energy(key)
            energy_ctr = energy_list.index(energy)
            intensity = self.get_intensity(key)
            intensity_ctr = intensity_list.index(intensity)
            model[energy_ctr,intensity_ctr] = self.hl_pm_model[key_ctr]

            for dev_ctr,dev in enumerate(self.devs_list):
                hl[dev_ctr,energy_ctr,intensity_ctr] = self.hl_pm_measured[key_ctr,dev_ctr]
                hl_total[dev_ctr,energy_ctr,intensity_ctr] = hl[dev_ctr,energy_ctr,intensity_ctr] + model[energy_ctr,intensity_ctr]
                uncertainty[dev_ctr,energy_ctr,intensity_ctr] = self.dev_pm_uncertainty[key_ctr,dev_ctr]

        self.hl, self.hl_total, self.uncertainty, self.model = hl, hl_total, uncertainty, model

    def _plot_devs(self):

        # One subplot for every device (quad or arc)
        for dev_ctr, dev in enumerate(self.devs_list):
            if dev_ctr%4 == 0:
                fig = plt.figure()
                title = 'Measured HL for %s %i' % (self.name, int(dev_ctr/4)+1)
                fig.canvas.set_window_title(title)
                plt.suptitle(title, fontsize=25)

            sp_nr = dev_ctr%4 + 1
            sp = plt.subplot(2,2,sp_nr)
            sp.set_ylabel('Heat Load [W/m]')
            sp.set_xlabel('Bunch Intensity [p+]')
            sp.set_title(dev)
            sp.set_xlim(0.6e11,1.2e11)

            colors = itertools.cycle(plt.rcParams['axes.prop_cycle'])

            for energy_ctr, energy in enumerate(energy_list):
                color = colors.next()[u'color']
                this_hl = self.hl_total[dev_ctr,energy_ctr,:]
                this_uncertainty = self.uncertainty[dev_ctr,energy_ctr,:]
                lower = this_hl-this_uncertainty
                higher = this_hl+this_uncertainty

                sp.plot(intensity_list_float,this_hl, marker='x', label=energy, color=color)
                sp.fill_between(intensity_list_float,lower, higher, color=color, alpha=0.5)
                sp.plot(intensity_list_float, self.model[energy_ctr,:], marker='x', label=self.model_label, color=color, ls='--')

            if self.name == 'Arcs':
                sp2 = sp.twinx()
                sp2.grid('off')
                sp2.set_ylabel('Heat Load [W/hc]')
                yaxes_factor = self.length_dict[dev]
                lower, higher = sp.get_ylim()
                sp2.set_ylim((yaxes_factor*lower, yaxes_factor*higher))
            if sp_nr == 2:
                sp.legend(bbox_to_anchor=(1.1, 1))

        # Everything in 1 plot
        fig = plt.figure()
        title = 'Measured HL for all %s, e-cloud only' % self.name
        fig.canvas.set_window_title(title)
        plt.suptitle(title, fontsize=25)

        for energy_ctr, energy in enumerate(energy_list):
            sp = plt.subplot(2,2,energy_ctr+1)
            sp.set_ylabel('Heat Load [W/m]')
            sp.set_xlabel('Bunch Intensity [p+]')
            sp.set_title(energy)
            sp.set_xlim(0.6e11,1.2e11)

            for dev_ctr, dev in enumerate(self.devs_list):
                sp.plot(intensity_list_float,self.hl[dev_ctr,energy_ctr,:], marker='x', label=dev)

            if energy_ctr == 1:
                sp.legend(bbox_to_anchor=(1.1, 1))


def main(hl_pm_measured, hl_pm_measured_quads, dict_keys, arcs, quads, scenarios_labels_dict,
        get_intensity, get_energy, hl_pm_model_arcs, hl_pm_model_quads, arc_pm_uncertainty, quad_pm_uncertainty, len_arc_quad_dict):

    # Arcs
    Handle_devs(arcs, hl_pm_model_arcs, hl_pm_measured, arc_pm_uncertainty, get_energy, get_intensity, dict_keys, 'Arcs', len_arc_quad_dict, 'Imp+SR')

    # Quads
    Handle_devs(quads, hl_pm_model_quads, hl_pm_measured_quads, quad_pm_uncertainty, get_energy, get_intensity, dict_keys, 'Quadrupoles', len_arc_quad_dict, 'Imp')

