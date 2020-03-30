import networkx as nx
import numpy as np
from random import sample
from networkx.algorithms.traversal.depth_first_search import dfs_tree
from networkx.drawing.nx_agraph import write_dot, graphviz_layout
import warnings
import momi

# subtree pruning and regrafting　(probably a submodule of mcmc)
def retrieve_inner_nodes(graph):
    nodes = graph.nodes()
    inner = [x for x in nodes if graph.out_degree(x)==2 and graph.in_degree(x)==1]
    return inner

def find_target_subgraph(graphs, exclude_node):
    # for now not included in a class
    graphs = graphs.to_undirected()
    graphs = list(nx.connected_component_subgraphs(graphs))
    if exclude_node in graphs[0].nodes:
        graph = graphs[1]
    elif exclude_node in graphs[1].nodes:
        graph = graphs[0]
    else:
        raiseValueError('something went wrong!')
    return graph

def draw_random_inner_node(graph):
    nodes = graph.nodes()
    inner = [x for x in nodes if graph.out_degree(x)==2 and graph.in_degree(x)==1]
    return sample(inner, 1)[0]

def draw_random_nonroot_node(graph):
    nodes = graph.nodes()
    inner = [x for x in nodes if graph.in_degree(x) > 0]
    return sample(inner, 1)[0]

def draw_random_branch(graph):
    return sample(graph.edges, 1)[0]

def SPR(graph, force_draw_node = None, print_output = False):
    '''
    subtree pruning and regrafting 
    '''
    topology = graph.copy()
    original_edges = topology.edges
    # detach a subtree
    chosen_node_prune = draw_random_nonroot_node(topology)
    parent_chosen_node_prune = next(topology.predecessors(chosen_node_prune))
    
    if force_draw_node:
        chosen_node_prune = force_draw_node
        parent_chosen_node_prune = next(topology.predecessors(chosen_node_prune))
    else:
        while topology.in_degree(parent_chosen_node_prune) == 0:
            chosen_node_prune = draw_random_nonroot_node(topology)
            parent_chosen_node_prune = next(topology.predecessors(chosen_node_prune))        


    reconnect_node_1 = next(topology.predecessors(parent_chosen_node_prune))
    reconnect_node_2 = topology.successors(parent_chosen_node_prune)
    reconnect_node_2 = [r for r in reconnect_node_2 if r != chosen_node_prune][0]

    topology.remove_node(parent_chosen_node_prune)
    topology.add_edge(reconnect_node_1, reconnect_node_2)

    # find a brach to insert the detached subtree
    subgraph_left = find_target_subgraph(topology, chosen_node_prune)
    branch_to_attach = draw_random_branch(subgraph_left)
    if branch_to_attach not in original_edges:
        branch_to_attach = (branch_to_attach[1], branch_to_attach[0])
    # 1) pruned subtree must be younger than the branch 2) must be a  different topology
    cond1 = topology.nodes[branch_to_attach[0]]['t_coalesce'] < topology.nodes[chosen_node_prune]['t_coalesce']
    cond2 = (set(branch_to_attach) == set((reconnect_node_1, reconnect_node_2)))
    while cond1 | cond2:
        branch_to_attach = draw_random_branch(subgraph_left)
        if branch_to_attach not in original_edges:
            branch_to_attach = (branch_to_attach[1], branch_to_attach[0])
        cond1 = topology.nodes[branch_to_attach[0]]['t_coalesce'] < topology.nodes[chosen_node_prune]['t_coalesce']
        cond2 = (set(branch_to_attach) == set((reconnect_node_1, reconnect_node_2)))
    
 
    topology.remove_edge(*branch_to_attach)

    topology.add_edge(branch_to_attach[0],parent_chosen_node_prune)
    topology.add_edge(parent_chosen_node_prune, branch_to_attach[1])
    topology.add_edge(parent_chosen_node_prune, chosen_node_prune)

    # get random time
    lower = max(topology.nodes[branch_to_attach[1]]['t_coalesce'], topology.nodes[chosen_node_prune]['t_coalesce'])
    upper = topology.nodes[branch_to_attach[0]]['t_coalesce']
    t = np.random.uniform(lower, upper)
    # add random time as the node attribute
    nx.set_node_attributes(topology, {parent_chosen_node_prune: t}, 't_coalesce')
    if print_output:
        print(f'detach node {chosen_node_prune}; regraft to branch {branch_to_attach}')
    return topology



# networkx graph object to momi demography object
def retrieve_events(graph):
    '''
    retrieve a list of tuples (node, event_time)
    '''
    events = []
    for n, t in list(graph.nodes(data=True)):
        if t['t_coalesce'] > 0:
            events.append((n, t['t_coalesce']))
    return sorted(events, key=lambda t: t[1])

def retrieve_leaf_nodes(graph):
    '''
    retrieve a list leave nodes
    '''
    nodes = graph.nodes()
    leaves = [x for x in nodes if graph.out_degree(x) == 0]
    return leaves 

def set_leaves_attribute_at_leaves(graph):
    '''
    set the leaves attribute as itself for leaf nodes
    '''
    leaves = retrieve_leaf_nodes(graph)
    leaves_dict = dict()
    for i, n in enumerate(leaves):
        leaves_dict[n] = leaves[i]
    nx.set_node_attributes(graph, leaves_dict, 'leaves')

def set_leaves_attribute(graph):
    '''
    recursively find the leaves under a node
    '''
    set_leaves_attribute_at_leaves(graph)
    events = retrieve_events(graph)
    for e in events:
        leaves_dict = nx.get_node_attributes(graph, 'leaves')
        children = list(graph.successors(e[0])) # get left and right child
        child_leaves = leaves_dict[children[1]] # leaves of the right child
        nx.set_node_attributes(graph, {e[0]: child_leaves}, 'leaves')

def graph2demography(graph, initialize = False, print_events = False):
    '''
    convert a networkx graph into a momi demography object
    '''
    model = momi.DemographicModel(N_e=1e4, gen_time=29, 
        muts_per_gen=1.25e-8)
    leaves = retrieve_leaf_nodes(graph)
    for l in leaves:
        model.add_leaf(l, t=0)

    set_leaves_attribute(graph)
    events = retrieve_events(graph)
    leaves_dict = nx.get_node_attributes(graph, 'leaves')
    for e in events:
        model.add_time_param(e[0])
        children = list(graph.successors(e[0]))
        model.move_lineages(leaves_dict[children[0]], 
            leaves_dict[children[1]], t = e[0])
        
        if initialize:
            model.set_params({e[0]: e[1]})
            if print_events:
                print(f'move from {leaves_dict[children[0]]} to {leaves_dict[children[1]]} at t = {e[1]:.2f}')
        else:
            if print_events:
                print(f'move from {leaves_dict[children[0]]} to {leaves_dict[children[1]]}')

    return model


# MCMC
def theta_proposal(theta_current, proposal_sigmas):
    ts = []
    for i, t in enumerate(theta_current):
        mu = t[1] 
        ts.append((t[0], max(np.random.normal(mu, proposal_sigmas[i], 1)[0], 50)))
    return ts

def theta_proposal_multiplicative(theta_current, scale = 10):
    ts = []
    shrink = np.random.binomial(1, 0.5)
    if shrink:
        scale = 1/scale
    for i, t in enumerate(theta_current):
        ts.append((t[0], scale * t[1]))
    return ts, scale

def initialize_mcmc_trace(graph):
    events = retrieve_events(graph)
    params = [events]
    topology = [1]
    return topology, params


def retrieve_event_time(graph, node):
    return graph.nodes[node]['t_coalesce']

def event_order_feasible(graph, event_dict):
    nx.set_node_attributes(graph, event_dict, 't_coalesce')
    events = retrieve_events(graph)
    for e in events:
        e_time = e[1]
        children = graph.successors(e[0])
        for c in children:
            if e_time < retrieve_event_time(graph, c):
                return False
    return True

def update_theta(theta, model):
    theta = dict(theta)
    model.set_params(theta)