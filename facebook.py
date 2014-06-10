#!/usr/bin/env python
import networkx as nx
import numpy as np
import glob
import os, os.path

feat_file_name = "feature_map.txt"
feature_index = {}  #numeric index to name
inverted_feature_index = {} #name to numeric index
network = nx.DiGraph()

def parse_featname_line(line):
    line = line[(line.find(' '))+1:]  # chop first field
    split = line.split(';')
    name = ';'.join(split[:-1]) # feature name
    index = int(split[-1].split(" ")[-1]) #feature index
    return index, name

def load_features():
    # may need to build the index first
    if not os.path.exists(feat_file_name):
        feat_index = {}
        # build the index from data/*.featnames files
        featname_files = glob.iglob("data/*.featnames")
        for featname_file_name in featname_files:
            featname_file = open(featname_file_name, 'r')
            for line in featname_file:
                # example line:
                # 0 birthday;anonymized feature 376
                index, name = parse_featname_line(line)
                feat_index[index] = name
            featname_file.close()
        keys = feat_index.keys()
        keys.sort()
        out = open(feat_file_name,'w')
        for key in keys:
            out.write("%d %s\n" % (key, feat_index[key]))
        out.close()
        
    # index built, read it in (even if we just built it by scanning)
    global feature_index
    global inverted_feature_index
    index_file = open(feat_file_name,'r')
    for line in index_file:
        split = line.strip().split(' ')
        key = int(split[0])
        val = split[1]
        feature_index[key] = val
    index_file.close()

    for key in feature_index.keys():
        val = feature_index[key]
        inverted_feature_index[val] = key

def load_nodes():
    assert len(feature_index) > 0, "call load_features() first"
    global network

    # get all the node ids by looking at the files
    node_ids = [int(x.split("/")[-1].split('.')[0]) for x in glob.glob("data/*.featnames")]

    # parse each node
    for node_id in node_ids:
        featname_file = open("data/%d.featnames" % node_id,'r')
        feat_file     = open("data/%d.feat" % node_id,'r')
        egofeat_file  = open("data/%d.egofeat" % node_id,'r')
        edge_file     = open("data/%d.edges" % node_id, 'r')

        # parse ego node
        network.add_node(node_id)
        # 0 1 0 0 0 ...
        ego_features = [int(x) for x in egofeat_file.readline().split(' ')]
        i = 0
        for line in featname_file:
            key, val = parse_featname_line(line)
            network.node[node_id][key] = ego_features[i]
            i += 1

        # parse neighboring nodes
        for line in feat_file:
            featname_file.seek(0)
            split = [int(x) for x in line.split(' ')]
            node_id = split[0]
            features = split[1:]
            network.add_node(node_id)
            i = 0
            for line in featname_file:
                key, val = parse_featname_line(line)
                network.node[node_id][key] = features[i]
                i += 1
            
        featname_file.close()
        feat_file.close()
        egofeat_file.close()
        edge_file.close()

def load_edges():
    global network
    assert network.order() > 0, "call load_nodes() first"
    edge_file = open("facebook_combined.txt","r")
    for line in edge_file:
        # nodefrom nodeto
        split = [int(x) for x in line.split(" ")]
        node_from = split[0]
        node_to = split[1]
        network.add_edge(node_from, node_to)

def load_network():
    load_features()
    load_nodes()
    load_edges()

if __name__ == '__main__':
    print "Running tests."
    print "Loading network..."
    load_network()
    print "done."
    
    def test(predicate, test_name):
        print "testing %s..." % (test_name,)
        assert predicate, "%s failed!" % (test_name,)
        print "%s passed." % (test_name,)

    test(network.order() == 4039, "order")
    test(network.size() == 88234, "size")
    
    print "All tests passed."
