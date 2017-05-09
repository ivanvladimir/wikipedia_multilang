#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Transforms docs into itf documents
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2015/IIMAS/UNAM
# ----------------------------------------------------------------------
# wiki2corpus.py is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# -------------------------------------------------------------------------

from __future__ import print_function

# System libraries
import argparse
import sys
import os.path
from smh import listdb_load, rng_init, SMHDiscoverer, rng_init
import re
import codecs
import json


if __name__ == "__main__":
    # Command line options
    p = argparse.ArgumentParser("Creates a corpus for topic discovery")

    p.add_argument("--idir",default='data',
            action="store", dest="idir",
            help="Input dir for documents [data]")
    p.add_argument("--odir",default='data',
            action="store", dest="odir",
            help="Output dir for documents [data]")
    p.add_argument("-v", "--verbose",
        action="store_true", dest="verbose", default=False,
        help="Verbose mode")
    p.add_argument("TOPICS",default=None,
        action="store", help="TOPICS")
    p.add_argument("LANG",nargs="+",
            help="Wikipedia language code")
    args = p.parse_args()

    # prepara función de verbose
    if args.verbose:
        def verbose(*args):
            print(*args)
    else:   
        verbose = lambda *a: None 

    idx2word={}
    idx2lang={}
    word2idx={}
    # Reading vocabulariesa
    verbose("Reading vocabulary")
    for lang in args.LANG:
    	verbose("Reading vocabulary",lang)
        with codecs.open(os.path.join(args.idir,"{0}wiki.voca".format(lang)),encoding='iso8859') as LANG:
            for line in LANG:
                bits=line.strip().split(" = ")
                w=bits[0]
                idx=int(bits[1])
                idx2word[idx]=w
                word2idx[w]=idx
                idx2lang[idx]=lang
                
    verbose("Loading topics:",args.TOPICS)
    topics=listdb_load(args.TOPICS)
    topics_=[]
    for topic in topics.ldb:
        topic_={}
        topic_['id']=len(topics_)
        words=[]
        for term in topic:
            topic__={}
            idx=int(term.item)
            freq=term.freq
            topic__['Word']=idx2word[idx]  
            topic__['Language']=idx2lang[idx]  
            topic__['Ocurrences']=freq  
            words.append(topic__)
        topic_['words']=words
        topics_.append(topic_)

    basename=os.path.basename(args.TOPICS)
    prefix=basename.rsplit('.',1)[0]
    filename_json=os.path.join(args.odir,"{0}.json".format(prefix))

    with open(filename_json,'w') as JSON:
        json.dump(topics_, JSON, sort_keys=True,
                indent=4, separators=(',', ': '))


