from json import load
import networkx as nx
import matplotlib.pyplot as plt

deltaZ = 1


def getGraph(data):
    G = nx.DiGraph()
    for i in range(0, len(data['points'])):
        G.add_node(str(i) + '0')
        G.add_node(str(i) + '1')
        G.add_edge(str(i) + '1', str(i) + '0', weight=deltaZ)
        G.add_edge(str(i) + '0', str(i) + '1', weight=deltaZ)

    for i in data['lines']:
        weight = ((data['points'][int(i['1'])]['x'] - data['points'][int(i['2'])][
            'x']) ** 2 + (data['points'][int(i['1'])]['y'] - data['points'][int(i['2'])]['y']) ** 2) ** 0.5
        G.add_edge(str(i['1']) + '0', str(i['2']) + '0', weight=weight)
        G.add_edge(str(i['2']) + '1', str(i['1']) + '1', weight=weight)
    return G


with open('static/roads.json', 'r') as f:
    G = getGraph(load(f))


def renew():
    global G
    with open('static/roads.json', 'r') as f:
        G = getGraph(load(f))


def build_path(p1, p2):
    return nx.shortest_path(G, source=p1, target=p2)


def printttt():
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'), node_size=500)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, edge_color='r', arrows=True)
    nx.draw_networkx_edges(G, pos, arrows=False)
    plt.show()
