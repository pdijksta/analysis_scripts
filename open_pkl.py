import cPickle

with open('./heatload_arcs.pkl') as f:
    pkl = cPickle.load(f)
with open('./heatload_pyecloud.pkl') as f:
    pkl2 = cPickle.load(f)
