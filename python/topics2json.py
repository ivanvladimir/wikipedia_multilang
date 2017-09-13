
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
from collections import Counter


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

    # prepara funcion de verbose
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
        with codecs.open(os.path.join(args.idir,"{0}wiki.voca".format(lang)),encoding='utf8') as LANG:
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
    topics__=[]
    objects={}
    for topic in topics.ldb:
        topic_={}
        topic_['id']=len(topics_)
        words=[]
        objects={}
        words_=Counter()
        for term in topic:
            topic__={}
            idx=int(term.item)
            freq=term.freq
            topic__['Word']=idx2word[idx]  
            topic__['Language']=idx2lang[idx]  
            topic__['Occurrences']=freq
            try:
               objects[idx2lang[idx]]+=freq
            except KeyError:
               objects[idx2lang[idx]]=freq
            words.append(topic__)
            words_[idx2word[idx]]=freq
        if args.min and len(words)<args.min:
            continue
        topic_['details']=[]
        topic_['topwords']=[w for w,x in words_.most_common(10)]
        size=0
        for k,v in  objects.items():
             topic_['details'].append({'Language':k,'NumberOfWords':v})
             size+=v
        topic_['size']=size
        topics_.append(topic_)
        topics__.append([])
        topics__[-1]={
                "id":len(topics_),
                "words":words,
                "details":topic_['details']
            }

    basename=os.path.basename(args.TOPICS)
    prefix=basename.rsplit('.',1)[0]
    filename_json=os.path.join(args.odir,"{0}.json".format(prefix))

    with codecs.open(filename_json,'w','utf8') as JSON:
        json.dump(topics_, JSON, sort_keys=True,ensure_ascii=False,
        encoding="utf-8",indent=4, separators=(',', ': '))

    for topic in topics__:
        with codecs.open(str(topic['id'])+".json",'w','utf8') as JSON:
            json.dump(topic, JSON, sort_keys=True,ensure_ascii=False,
            encoding="utf-8",indent=4, separators=(',', ': '))


