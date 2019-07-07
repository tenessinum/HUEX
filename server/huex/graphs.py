from json import load
import networkx as nx
import matplotlib.pyplot as plt


def getGraph(data):
    G = nx.DiGraph()
    for i in range(0, len(data['points'])):
        G.add_node(i)
    for i in data['lines']:
        G.add_edge(int(i['1']), int(i['2']), weight=((data['points'][int(i['1'])]['x'] - data['points'][int(i['2'])][
            'x']) ** 2 + (data['points'][int(i['1'])]['y'] - data['points'][int(i['2'])]['y']) ** 2) ** 0.5)
    return G


with open('../static/roads.json', 'r') as f:
    G = getGraph(load(f))

pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'), node_size=500)
nx.draw_networkx_labels(G, pos)
nx.draw_networkx_edges(G, pos, edge_color='r', arrows=True)
nx.draw_networkx_edges(G, pos, arrows=False)
plt.show()
