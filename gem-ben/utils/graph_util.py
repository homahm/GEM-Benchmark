try: import cPickle as pickle
except: import pickle
import numpy as np
import networkx as nx
import random
import itertools
from time import time
import pdb



def transform_DiGraph_to_adj(di_graph):
    n = di_graph.number_of_nodes()
    adj = np.zeros((n, n))
    for st, ed, w in di_graph.edges(data='weight', default=1):
        adj[st, ed] = w
    return adj


def transform_adj_to_DiGraph(adj):
    n = adj.shape[0]
    di_graph = nx.DiGraph()
    di_graph.add_nodes_from(range(n))
    for i in xrange(n):
        for j in xrange(n):
            if(i != j):
                if(adj[i, j] > 0):
                    di_graph.add_edge(i, j, weight=adj[i, j])
    return di_graph


def get_lcc(di_graph):
    di_graph = di_graph.to_undirected().to_directed()
    di_graph = max(nx.weakly_connected_component_subgraphs(di_graph), key=len)
    tdl_nodes = di_graph.nodes()
    nodeListMap = dict(zip(tdl_nodes, range(len(tdl_nodes))))
    di_graph = nx.relabel_nodes(di_graph, nodeListMap, copy=True)
    return di_graph, nodeListMap


def get_lcc_undirected(G):
    G2 = max(nx.connected_component_subgraphs(G), key=len)
    tdl_nodes = G2.nodes()
    nodeListMap = dict(zip(tdl_nodes, range(len(tdl_nodes))))
    G2 = nx.relabel_nodes(G2, nodeListMap, copy=True)
    return G2, nodeListMap

def get_nk_lcc_undirected(G):
    G2 = max(nx.connected_component_subgraphs(G), key=len)
    tdl_nodes = G2.nodes()
    nodeListMap = dict(zip(tdl_nodes, range(len(tdl_nodes))))
    G2 = nx.relabel_nodes(G2, nodeListMap, copy=True)
    return G2, nodeListMap

def print_graph_stats(G):
    print('# of nodes: %d, # of edges: %d' % (G.number_of_nodes(),
                                              G.number_of_edges()))


def sample_graph_rw(di_graph, n_sampled_nodes=None,
                    random_res_p=0.01, verbose=False):
    t1 = time()
    print('\t\tRandom walk sampling. # nodes to sample: %d' % n_sampled_nodes)
    node_num = di_graph.number_of_nodes()
    node_l = [[]] * n_sampled_nodes
    s_node_idx = 0
    if n_sampled_nodes and node_num > n_sampled_nodes:
        # Choose the first node such that it has an outgoing edge
        tempNb = []
        while not tempNb:
            curr_node = np.random.random_integers(node_num) - 1
            tempNb = di_graph.neighbors(curr_node)
        node_l[s_node_idx] = curr_node
        s_node_idx += 1
        while s_node_idx < n_sampled_nodes:
            # # node_l_inv = {v: k for k, v in enumerate(node_l[:s_node_idx])}
            # # sampled_graph = nx.DiGraph()
            # # sampled_graph.add_nodes_from(range(n_sampled_nodes))
            # # for st, ed, w in di_graph.edges_iter(data='weight', default=1):
            # #     try:
            # #         v_i = node_l_inv[st]
            # #         v_j = node_l_inv[ed]
            # #         sampled_graph.add_edge(v_i, v_j, weight=w)
            # #     except:
            # #         continue
            # if verbose:
            #     print('Sample edges: %d, total edges: %d' % (sampled_graph.number_of_edges(), di_graph.number_of_edges()))
            # if sampled_graph.number_of_edges() == di_graph.number_of_edges():
            #     break
            if verbose:
                print('\t\t\t# nodes sampled: %d' % s_node_idx)
            try:
                random_restart = np.random.rand()
                if random_restart < random_res_p:
                    tempNb = []
                    while not tempNb:
                        new_sampled_node = \
                            np.random.random_integers(node_num) - 1
                        tempNb = di_graph.neighbors(new_sampled_node)
                else:
                    new_sampled_node = np.random.choice(
                        di_graph.neighbors(curr_node)
                    )
            except ValueError:
                # Restart if there is no outgoing edge
                tempNb = []
                while not tempNb:
                    new_sampled_node = np.random.random_integers(node_num) - 1
                    tempNb = di_graph.neighbors(new_sampled_node)
            curr_node = new_sampled_node
            if curr_node not in node_l[:s_node_idx]:
                node_l[s_node_idx] = new_sampled_node
                s_node_idx += 1
        try:
            node_l_inv = {v: k for k, v in enumerate(node_l[:s_node_idx])}
        except:
            pdb.set_trace()
        sampled_graph = nx.DiGraph()
        sampled_graph.add_nodes_from(range(s_node_idx))
        for st, ed, w in di_graph.edges.data('weight', default=1):
            try:
                v_i = node_l_inv[st]
                v_j = node_l_inv[ed]
                sampled_graph.add_edge(v_i, v_j, weight=w)
            except:
                continue
        print('\t\tSampled graph: n-%d, m-%d, time taken: %f sec' % (
            sampled_graph.number_of_nodes(),
            sampled_graph.number_of_edges(),
            time() - t1)
        )
        return sampled_graph, node_l
    else:
        print('\t\tSampled graph: n-%d, m-%d, time taken: %f sec' % (
            di_graph.number_of_nodes(),
            di_graph.number_of_edges(),
            time() - t1)
        )
        return di_graph, np.arange(di_graph.number_of_nodes())


def sample_graph(di_graph, n_sampled_nodes=None):
    node_num = di_graph.number_of_nodes()
    if n_sampled_nodes and node_num > n_sampled_nodes:
        node_l = np.random.choice(node_num, n_sampled_nodes, replace=False)
        node_l_inv = {v: k for k, v in enumerate(node_l)}
        sampled_graph = nx.DiGraph()
        sampled_graph.add_nodes_from(range(n_sampled_nodes))
        for st, ed, w in di_graph.edges(data='weight', default=1):
            try:
                v_i = node_l_inv[st]
                v_j = node_l_inv[ed]
                sampled_graph.add_edge(v_i, v_j, weight=w)
            except:
                continue
        return sampled_graph, node_l
    else:
        return di_graph, np.arange(di_graph.number_of_nodes())


def randwalk_DiGraph_to_adj(di_graph, node_frac=0.1,
                            n_walks_per_node=5, len_rw=2):
    t0 = time.time()
    n = di_graph.number_of_nodes()
    adj = np.zeros((n, n))
    rw_node_num = int(node_frac * n)
    rw_node_list = np.random.choice(n, size=[rw_node_num],
                                    replace=False, p=None)
    for node in rw_node_list:
        for walk in range(n_walks_per_node):
            cur_node = node
            for step in range(len_rw):
                cur_neighbors = di_graph.neighbors(cur_node)
                try:
                    neighbor_node = np.random.choice(cur_neighbors)
                except:
                    continue
                try:
                    adj[cur_node, neighbor_node] = di_graph.get_edge_data(
                        cur_node,
                        neighbor_node
                    )['weight']
                    adj[neighbor_node, cur_node] = di_graph.get_edge_data(
                        cur_node,
                        neighbor_node
                    )['weight']
                except KeyError:
                    adj[cur_node, neighbor_node] = 1
                    adj[neighbor_node, cur_node] = 1
                cur_node = neighbor_node
    print('Time taken for random walk  on {0} nodes = {1}'.format(n, time.time() - t0))
    return adj


def addChaos(di_graphs, k):
    anomaly_time_steps = sorted(random.sample(range(len(di_graphs)), k))
    for t in anomaly_time_steps:
        n = di_graphs[t].number_of_nodes()
        e = di_graphs[t].number_of_edges()
        di_graphs[t] = nx.fast_gnp_random_graph(n, e / float(n * (n - 1)),
                                                seed=None, directed=False)
        di_graphs[t] = di_graphs[t].to_directed()
    return di_graphs, anomaly_time_steps


def addNodeAnomalies(di_graphs, p, k):
    anomaly_time_steps = sorted(random.sample(range(len(di_graphs)), k))
    for t in anomaly_time_steps:
        n_nodes = di_graphs[t].number_of_nodes()
        anomalous_nodes_idx = np.random.choice([0, 1],
                                               size=(n_nodes, 1),
                                               p=(1 - p, p))
        node_list = np.array(di_graphs[t].nodes())
        node_list = node_list.reshape((n_nodes, 1))
        anomalous_nodes = np.multiply(anomalous_nodes_idx, node_list)
        anomalous_nodes = anomalous_nodes[anomalous_nodes > 0]
        # pdb.set_trace()
        di_graphs[t].add_edges_from(
            itertools.product(list(anomalous_nodes), range(n_nodes))
        )
        di_graphs[t].add_edges_from(
            itertools.product(range(n_nodes), list(anomalous_nodes))
        )
        print('Nodes: %d, Edges: %d' % (di_graphs[t].number_of_nodes(),
                                        di_graphs[t].number_of_edges()))
    return anomaly_time_steps


def saveGraphToEdgeListTxt(graph, file_name):
    with open(file_name, 'w') as f:
        f.write('%d\n' % graph.number_of_nodes())
        f.write('%d\n' % graph.number_of_edges())
        for i, j, w in graph.edges(data='weight', default=1):
            f.write('%d %d %f\n' % (i, j, w))



def convertNkToNx(G_nk):
    G_nx = nx.Graph()
    for i, j in G_nk.edges():
        G_nx.add_edge(i,j)
    return G_nx

def saveGraphToEdgeListTxtn2v(graph, file_name):
    with open(file_name, 'w') as f:
        for i, j, w in graph.edges(data='weight', default=1):
            f.write('%d %d %f\n' % (i, j, 1))


def loadGraphFromEdgeListTxt(file_name, directed=True):
    with open(file_name, 'r') as f:
        # n_nodes = f.readline()
        # f.readline() # Discard the number of edges
        if directed:
            G = nx.DiGraph()
        else:
            G = nx.Graph()
        for line in f:
            edge = line.strip().split()
            if len(edge) == 3:
                w = float(edge[2])
            else:
                w = 1.0
            G.add_edge(int(edge[0]), int(edge[1]), weight=w)
    return G


def loadEmbedding(file_name):
    with open(file_name, 'r') as f:
        n, d = f.readline().strip().split()
        X = np.zeros((int(n), int(d)))
        for line in f:
            emb = line.strip().split()
            emb_fl = [float(emb_i) for emb_i in emb[1:]]
            X[int(emb[0]), :] = emb_fl
    return X


def loadSBMGraph(file_prefix):
    graph_file = file_prefix + '_graph.gpickle'
    G = nx.read_gpickle(graph_file)
    node_file = file_prefix + '_node.pkl'
    with open(node_file, 'rb') as fp:
        node_community = pickle.load(fp)
    return (G, node_community)


def loadRealGraphSeries(file_prefix, startId, endId):
    graphs = []
    for file_id in range(startId, endId + 1):
        graph_file = file_prefix + str(file_id) + '_graph.gpickle'
        graphs.append(nx.read_gpickle(graph_file))
    return graphs


def saveRealGraphSeries(G, file_prefix='graphs/day_'):
    for idx in range(len(G)):
        f_name = file_prefix + str(idx) + "_graph.gpickle"
        # cPickle.dump(G[idx], open(f_name, 'wb'))
        nx.write_gpickle(G[idx], f_name)


def loadDynamicSBmGraph(file_perfix, length):
    graph_files = ['%s_%d_graph.gpickle' % (file_perfix, i) for i in xrange(length)]
    info_files = ['%s_%d_node.pkl' % (file_perfix, i) for i in xrange(length)]

    graphs = [nx.read_gpickle(graph_file) for graph_file in graph_files]

    nodes_comunities = []
    perturbations = []
    for info_file in info_files:
        with open(info_file, 'rb') as fp:
            node_infos = pickle.load(fp)
            nodes_comunities.append(node_infos['community'])
            perturbations.append(node_infos['perturbation'])

    return zip(graphs, nodes_comunities, perturbations)


def saveDynamicSBmGraph(file_perfix, dynamic_graphs):
    length = len(dynamic_graphs)
    graph_files = ['%s_%d_graph.gpickle' % (file_perfix, i) for i in xrange(length)]
    info_files = ['%s_%d_node.pkl' % (file_perfix, i) for i in xrange(length)]

    for i in xrange(length):
        # save graph
        nx.write_gpickle(dynamic_graphs[i][0], graph_files[i])
        # save additional node info
        with open(info_files[i], 'wb') as fp:
            node_infos = {}
            node_infos['community'] = dynamic_graphs[i][1]
            node_infos['perturbation'] = dynamic_graphs[i][2]
            pickle.dump(node_infos, fp)
