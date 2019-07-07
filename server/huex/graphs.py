from json import load
import networkx as nx


def getGraph(data):
    G = nx.DiGraph()
    for i in range(0, len(data['points'])):
        G.add_node(i)
    for i in data['lines']:
        weight = ((data['points'][int(i['1'])]['x'] - data['points'][int(i['2'])][
            'x']) ** 2 + (data['points'][int(i['1'])]['y'] - data['points'][int(i['2'])]['y']) ** 2) ** 0.5
        G.add_edge(int(i['1']), int(i['2']), weight=weight)
    return G


with open('static/roads.json', 'r') as f:
    G = getGraph(load(f))


def renew():
    global G
    with open('static/roads.json', 'r') as f:
        G = getGraph(load(f))


def build_path(p1, p2):
    return nx.shortest_path(G, source=p1, target=p2)
