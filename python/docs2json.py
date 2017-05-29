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
from sklearn.metrics.pairwise import pairwise_distances


if __name__ == "__main__":
    # Command line options
    p = argparse.ArgumentParser("Creates a corpus for topic discovery")

    p.add_argument("--idir",default='data',
            action="store", dest="idir",
            help="Input dir for documents [data]")
    p.add_argument("--odir",default='data',
            action="store", dest="odir",
            help="Output dir for documents [data]")
    p.add_argument("--min",default=None,type=int,
            action="store", dest="min",
            help="Minumum number of terms in topics [0]")
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
    index={}
    # Reading vocabulariesa
    verbose("Reading vocabulary")
    for lang in args.LANG:
    	#  verbose("Reading vocabulary",lang)
        #  with open(os.path.join(args.idir,"{0}wiki.voca".format(lang))) as LANG:
        #      for line in LANG:
        #          bits=line.strip().split(" = ")
        #          w=bits[0]
        #          idx=int(bits[1])
        #          idx2word[idx]=w
        #          word2idx[w]=idx
        #          idx2lang[idx]=lang

        verbose("Reading index",lang)
        with open(os.path.join(args.idir,"{0}wiki.index".format(lang))) as INDEX:
            for idd,line in enumerate(INDEX):
                bits=line.strip().split(" == ")
                pos=int(bits[0])
                idx=int(bits[1])
                url=bits[2]
                title=bits[3]
                if not index.has_key(lang):
                    index[lang]={}
                index[lang][idd]=(pos,url,title)
  
    verbose("Loading topics:",args.TOPICS)
    topics=listdb_load(args.TOPICS)
    topics_=[]
    for topic in topics.ldb:
        idxs=set()
        for term in topic:
            idxs.add(int(term.item))
        if args.min and len(idxs)<args.min:
            continue
        topics_.append(idxs)

    topics_docs={}
    for lang in args.LANG:
        verbose("Procesing",lang)
        filename_corpus=os.path.join(args.idir,"{0}wiki.position.corpus".format(lang))
        for idoc,line in enumerate(codecs.open(filename_corpus)):
            doc_=[]
            bits=line.split(" ",4)
            for word in bits[4]:
                bits=line.split()
                term=int(bits[1].split()[0])
                doc_.append(term)
            if len(doc_)==0:
                continue
            doc_=set(doc_)
            for itopic,idxs in enumerate(topics_):
                if len(idxs)==0:
                    continue
                res=len(doc_.intersection(idxs))*1.0/max(len(doc_),len(idxs))
                if res>0.4:
                    try:
                        topics_docs[lang]
                    except KeyError:
                        topics_docs[lang]={}
                    try:
                        topics_docs[lang][itopic].append({'url':index[lang][idoc][1],'title':index[lang][idoc][2],'ol':res})
                    except KeyError:
                        topics_docs[lang][itopic]=[{'url':index[lang][idoc][1],'title':index[lang][idoc][2],'ol':res}]
            verbose("Finish procesing doc",idoc,lang)

    topics_docs_={}
    for lang in args.LANG:
        for itopic,ref in topics_docs[lang].iteritems():
            if not topics_docs_.has_key(itopic):
                topics_docs_[itopic]={}
            topics_docs_[itopic][lang]=sorted(ref, key = lambda k : k['ol'], reverse=True)
    
    basename=os.path.basename(args.TOPICS)
    prefix=basename.rsplit('.',1)[0]
    filename_json=os.path.join(args.odir,"{0}.docs.json".format(prefix))
   
    with codecs.open(filename_json,'w','utf8') as JSON:
        json.dump(topics_docs_, JSON, sort_keys=True,ensure_ascii=False,
        encoding="utf-8",indent=4, separators=(',', ': '))


