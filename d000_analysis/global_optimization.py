import numpy as np
import matplotlib.pyplot as plt

# Global optimization, deprecated
def main(dict_keys,arcs,sey_list,coast_strs,hl_measured,hl_pyecloud, length, devices):
    delta_sq = np.zeros(shape=(len(arcs),len(sey_list),len(coast_strs)))
    for arc_ctr in xrange(len(arcs)):
        for key_ctr in xrange(len(dict_keys)):
            measured = hl_measured[key_ctr,arc_ctr] * length['HalfCell']
            for coast_ctr in xrange(len(coast_strs)):
                pyecloud = 0
                for sey_ctr in xrange(len(sey_list)):
                    for device_ctr, device in enumerate(devices):
                        pyecloud += hl_pyecloud[key_ctr,device_ctr,coast_ctr,sey_ctr]*length[device]
                    delta_sq[arc_ctr,sey_ctr,coast_ctr] += ((measured-pyecloud)/measured)**2
    delta = np.sqrt(delta_sq/len(dict_keys))


    fig = plt.figure()
    title_str = 'Comparison of measured to pyecloud heat loads, %i scenarios' % len(dict_keys)
    fig.canvas.set_window_title(title_str)
    plt.suptitle(title_str, fontsize=20)

    for coast_ctr, coast_str in enumerate(coast_strs):
        subplot = plt.subplot(len(coast_strs),1,coast_ctr+1)

        subplot.set_ylim(0,5)
        subplot.set_title('Coasting Beam of %s' % coast_str)
        subplot.set_xlabel('SEY Parameter')
        subplot.set_ylabel('RMS deviation')

        for arc_ctr, label in enumerate(arcs):
            subplot.plot(sey_list, delta[arc_ctr,:,coast_ctr], label=label)
            subplot.legend(bbox_to_anchor=(1.1, 1))
