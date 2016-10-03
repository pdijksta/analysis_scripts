import numpy as np
import matplotlib.pyplot as plt

# Global optimization, deprecated
def main(dict_keys,arcs,sey_list,coast_strs,hl_measured,hl_pyecloud):
    delta_sq = np.zeros(shape=(len(arcs),len(sey_list),len(coast_strs)))
    for arc_ctr in xrange(len(arcs)):
        for key_ctr in xrange(len(dict_keys)):
            measured = hl_measured[key_ctr,arc_ctr]
            for coast_ctr in xrange(len(coast_strs)):
                for sey_ctr in xrange(len(sey_list)):
                    pyecloud = np.sum(hl_pyecloud[key_ctr,:,coast_ctr,sey_ctr])
                    delta_sq[arc_ctr,sey_ctr,coast_ctr] += ((measured-pyecloud)/measured)**2
    delta = np.sqrt(delta_sq/len(dict_keys))


    fig = plt.figure()
    title_str = 'Comparison of measured to pyecloud heat loads, %i scenarios' % len(dict_keys)
    fig.canvas.set_window_title(title_str)
    plt.suptitle(title_str, fontsize=16)

    coast_subplot = (plt.subplot(2,1,1), plt.subplot(2,1,2))

    for coast_ctr, coast_str in enumerate(coast_strs):
        subplot = coast_subplot[coast_ctr]

        subplot.set_ylim(0,5)
        subplot.set_title('Coasting Beam of %s' % coast_str)
        subplot.set_xlabel('SEY Parameter')
        subplot.set_ylabel('RMS deviation')

        for arc_ctr, label in enumerate(arcs):
            subplot.plot(sey_list, delta[arc_ctr,:,coast_ctr], label=label)
            subplot.legend()

    plt.subplots_adjust(right=0.7, wspace=0.30)

