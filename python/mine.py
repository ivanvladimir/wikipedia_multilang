#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Sampled MinHash demo with images
# ----------------------------------------------------------------------
# Gibran Fuentes-Pineda, Ivan V. Meza
# 2015/IIMAS, México
# ----------------------------------------------------------------------
from __future__ import print_function

import sys
from sklearn.base import BaseEstimator
from smh import listdb_load, rng_init, SMHDiscoverer, rng_init
import math
import os
import time
import random
timestr = time.strftime("%Y%m%d-%H%M%S")

def s2l(s,r):
    return int(math.log(0.5)/math.log(1-math.pow(s,r)))

class SMHTopicDiscovery(BaseEstimator):
    """
    SMH-based topic discovery.
    """
    def __init__(self,
                 tuple_size = 3,
                 number_of_tuples = None,
                 table_size = 2**24,
                 cooccurrence_threshold = 0.14, 
                 min_set_size = 3,
                 cluster_tuple_size = 3,
                 cluster_number_of_tuples = 255,
                 cluster_table_size = 2**24,
                 overlap = 0.8,
                 min_cluster_size = 3):

        self.tuple_size_ = tuple_size

        if number_of_tuples:
            self.cooccurrence_threshold_ = pow(1. -  pow(0.5, 1. / float(number_of_tuples)), 1. / float(tuple_size))
            self.number_of_tuples_ = number_of_tuples
        else:
            self.cooccurrence_threshold_ = cooccurrence_threshold
            self.number_of_tuples_ = int(math.log(0.5) / math.log(1.0 - pow(cooccurrence_threshold, tuple_size)))

        self.table_size_ = table_size
        self.min_set_size_ = min_set_size
        self.cluster_tuple_size_ = cluster_tuple_size
        self.cluster_number_of_tuples_ = cluster_number_of_tuples
        self.cluster_table_size_ = cluster_table_size
        self.overlap_ = overlap
        self.min_cluster_size_ = min_cluster_size
        self.discoverer_ = SMHDiscoverer(tuple_size = self.tuple_size_,
                                         number_of_tuples = self.number_of_tuples_,
                                         table_size = self.table_size_,
                                         cooccurrence_threshold = self.cooccurrence_threshold_, 
                                         min_set_size = self.min_set_size_,
                                         cluster_tuple_size = self.cluster_tuple_size_,
                                         cluster_number_of_tuples = self.cluster_number_of_tuples_,
                                         cluster_table_size = self.cluster_table_size_,
                                         overlap = self.overlap_,
                                         min_cluster_size = self.min_cluster_size_)


    def fit(self,
            X,
            weights = None,
            corpus = None):
        """
        Discovers topics from a text corpus.
        """
        self.models = self.discoverer_.fit(X,
                                           weights = weights,
                                           expand = corpus)


# MAIN program
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser("Mines")
    p.add_argument("-p","--params",default=[(2,120)],
                action="append", dest="params",type=float,nargs=2,
                help="(Size of the tuple, S*| number of tuples)")
    p.add_argument("-l","--number_tuples",default=False,
                action="store_true", dest="l",
                help="Turn on second value op pair as parameter l, otherwise s*")
    p.add_argument("--idir",default='data',
            action="store", dest="idir",
            help="Input dir for documents [data]")
    p.add_argument("--odir",default='data',
            action="store", dest="odir",
            help="Output dir for documents [data]")
    p.add_argument("--cutoff",default=None,type=int,
        action="store", dest='cutoff',help="Cutoff of topics [Off]")
    p.add_argument("--min_cluster_size",default=5,type=int,
            action="store", dest='min_cluster_size',help="Minimum size of cluster for default clustering[3]")
    p.add_argument("--thres",default=0.9,type=float,
            action="store", dest='thres',
            help="Threshold for clustering")
    p.add_argument("-v", "--verbose",
        action="store_true", dest="verbose", default=False,
        help="Verbose mode")
    p.add_argument("IFS",default=None,
        action="store", help="Inverted file structure of documents")
    p.add_argument("LANG",nargs="+",
            help="Wikipedia language code")
 
    opts = p.parse_args()

    # prepara función de verbose
    if opts.verbose:
        def verbose(*opts):
            print(*opts)
    else:   
        verbose = lambda *a: None 
    verbose("======================================= Starting point")
    rng_init(42)

    if len(opts.params)>1:
        opts.params.pop(0)

    idx2word={}
    word2idx={}
    # Reading vocabulariesa
    verbose("Reading vocabulary")
    for lang in opts.LANG:
    	verbose("Reading vocabulary",lang)
        with open(os.path.join(opts.idir,"{0}wiki.voca".format(lang))) as LANG:
            for line in LANG:
                bits=line.strip().split(" = ")
                w=bits[0]
                idx=int(bits[1])
                idx2word[idx]=w
                word2idx[w]=idx
                
    verbose("Loading file ifs:",opts.IFS)
    ifs=listdb_load(opts.IFS)

    if not opts.l:
        params=[(int(r),s2l(s,r),s) for r,s in opts.params]
    else:
        params=[(int(r),int(l),0) for r,l in opts.params]
    params.sort()

    cs=[]

    for r,l,s in params:
        verbose( "======================================= experiment for",r,l,s)
        if s>0:
            verbose( "Experiment tuples (r) {0}, Number of tuples (l) {1}, S* {2}".format(r,l,s))
        else:
            verbose("Experiment tuples (r) {0}, Number of tuples (l) {1}".format(r,l))

   	model = SMHTopicDiscovery(tuple_size = r,
                              table_size = 2**24,
                              number_of_tuples = l,
                              min_cluster_size= opts.min_cluster_size,
                              overlap = opts.thres)
        
	verbose("Discovering topics")    
    	start_time = time.time()
    	model.fit(ifs)
    	end_time = time.time()
    	total_time = end_time - start_time
	verbose("Total time",total_time)

	basename=os.path.basename(opts.IFS)
        prefix=basename.split('.',1)[0]
        filename_model=os.path.join(opts.odir,"{0}.r_{1}_l_{2}.model".format(prefix,r,l))
        verbose("Saving model to",filename_model)
        model.models.save(filename_model)

        filename_topics=os.path.join(opts.odir,"{0}.r_{1}_l_{2}.topics".format(prefix,r,l))
        verbose("Saving topics to",filename_topics)
        with open(filename_topics,'w') as TOPICS:
	    for m in model.models.ldb:
                terms = []
                for j in m:
                    terms.append(idx2word[j.item])
                print(", ".join(terms),file=TOPICS)
     

 


