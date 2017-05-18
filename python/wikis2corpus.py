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
import random
import re
import codecs
import nltk
random.seed()

from collections import Counter,defaultdict
punct=re.compile("[^\s]+", re.UNICODE)

def line2words(line,sws):
    return [w for w in nltk.word_tokenize(line.lower()) 
                if len(w)>0 and not w in sws]
 
if __name__ == "__main__":
    # Command line options
    p = argparse.ArgumentParser("Creates a corpus for topic discovery")
    p.add_argument("LANG",nargs="+",
            help="Wikipedia language code")
    p.add_argument("--idir",default='data',
            action="store", dest="idir",
            help="Input dir for documents [data]")
    p.add_argument("--odir",default='data',
            action="store", dest="odir",
            help="Output dir for documents [data]")
    p.add_argument("--swdir",default='stopwords',
            action="store", dest="swdir",
            help="stopword directory")
    p.add_argument("--min_per_doc",
        action="store", dest="min_per_doc", type=int,default=20,
        help="Minimum words per document [50]")
    p.add_argument("--cutoff",
        action="store", dest="cutoff", type=int,default=30,
        help="Cut off for frecuencies [10]")
    p.add_argument("--max",
        action="store", dest="max", type=int,default=None,
        help="Max number of documents to process [All]")
    p.add_argument("-v", "--verbose",
        action="store_true", dest="verbose", default=False,
        help="Verbose mode")
    args = p.parse_args()

    # prepara función de verbose
    if args.verbose:
        def verbose(*args):
            print(*args)
    else:   
        verbose = lambda *a: None 

    # Reading indexes
    linked=defaultdict(lambda : defaultdict(set))
    indices_docs=defaultdict(set)
    title_docs=defaultdict(set)
    verbose("Reading documents with links")
    for lang in args.LANG:
        with open(os.path.join(args.idir,"{0}wiki.links.csv".format(lang))) as FILE:
            for line in FILE:
                line=line.strip()
                bits=line.split(',')
                indices_docs[lang].add(int(bits[0]))
                title_docs[bits[1]].add(bits[2])
                linked[bits[1]][bits[2]].add(int(bits[0]))
        verbose("Documents with links in ",lang," ",len(indices_docs[lang]))

    
    verbose("Documents link to")
    for lang in args.LANG:
        verbose("Linked documents in ",lang," ",len(linked[lang]))

    order_indices=[(lang,len(doc)) for lang,doc in indices_docs.iteritems()]
    order_indices.sort(key=lambda tup: tup[1],reverse=True)

    # Reading stopwords
    sw={}
    for lang in args.LANG:
        sw[lang]=set()
        with open(os.path.join(args.swdir,"{0}.txt".format(lang))) as FILE:
            for line in FILE:
                line=line.strip()
                if line.startswith("#"):
                    continue
                sws=[w.strip() for w in line.split(',')]
                sw[lang].update(sws)
        verbose("Size of sw for ",lang," ",len(sw[lang]))
    
    
    verbose("Order of processing languages: ",", ".join([x for x,y in order_indices]))

    # Extrayendo los vocabularios
    re_header = re.compile(r'<doc id="(.*)" url="(.*)" title="(.*)">')
    re_slashdoc = re.compile('</doc>')
    re_number = re.compile('^\d+\w*$')
    voca={}
    vocab_doc={}
    doc={}
    index={}
    position=0
    positions={}
    positions_={}
    nvoca=0

    for lang in [x for x,y in order_indices]:
        verbose("Extracting articles ",lang)
        voca[lang]=Counter()
        vocab_doc[lang]=Counter()
        doc=Counter()
        index[lang]={}
        process=False
        total_docs=0
        total_docs_=0
    
        with codecs.open(os.path.join(args.idir,"{0}wiki.xml".format(lang)),'r','utf8') as FILE:
            for line in FILE:
                line=line.strip()
                m= re_header.match(line)
                if m:
                    if args.max and total_docs==args.max:
                        break
                    if total_docs and not total_docs%1000:
                        print('.',end="")
                    idx=int(m.group(1))
                    url=m.group(2)
                    title=m.group(3)
                    process=False
                    if (linked[lang].has_key(title)):
                        process=True
                    if process:
                        index[lang][idx]=(url,title)
                        if not positions.has_key(idx):
                            positions[idx]=position
                            for idx_ in linked[lang][title]:
                                positions[idx_]=position
                            position+=1
                elif re_slashdoc.match(line):
                    if process:
                        voca[lang].update(doc)
                        vocab_doc[lang].update(doc.keys())
                        total_docs_+=1
                    doc= Counter()
                    total_docs+=1
                else:
                    if process:
                        doc.update(line2words(line.strip(),sw[lang]))
            verbose("\nTotal number of documents ",lang," ",total_docs_," from ", total_docs) 
            verbose("Vocabulary size ",lang," ",len(voca[lang])) 
            verbose("Total number of words ",lang, " ",sum(voca[lang].values())) 

        verbose("\nCorpus for",lang)
        header=None
        docs={}
        total_docs=0

        vocab=[(w,n) for (w,n) in voca[lang].most_common() 
                if n>=args.cutoff and
                   (args.min_per_doc==0 or vocab_doc[lang][w]>=args.min_per_doc)
                   and len(w)>1
                   and not re_number.match(w)
                   and not w.startswith('formula_')
                   and not w.startswith('codice_')
                   ]
        vocab_={}
        for (i,(w,n)) in enumerate(vocab):
            vocab_[w]=i+nvoca
        total_docs_=0
        with codecs.open(os.path.join(args.idir,"{0}wiki.xml".format(lang)),'r','utf8') as FILE,\
             codecs.open(os.path.join(args.odir,"{0}wiki.position.corpus".format(lang)),'w','utf8') as CORPUS,\
             codecs.open(os.path.join(args.odir,"{0}wiki.index".format(lang)),'w','utf8') as INDEX:
                for line in FILE:
                    line=line.strip()
                    m= re_header.match(line)
                    if m:
                        if args.max and total_docs==args.max:
                            break
                        if total_docs and not total_docs%1000:
                            print('.',end="")
                        idx=int(m.group(1))
                        title=m.group(3)
                        process=False
                        if (linked[lang].has_key(title) and positions.has_key(idx) and index[lang].has_key(idx)):
                            process=True
                    elif re_slashdoc.match(line):
                        if process:
                            info=[(w,n) for w,n in doc.most_common() if vocab_.has_key(w)] 
                            #docs[positions[idx]]=(idx,info)
                            print(positions[idx]," ",len(info)," ".join(["{0}:{1}".format(vocab_[w],n) for w,n in info if vocab_.has_key(w)]),file=CORPUS)
                            print(positions[idx],"==",idx,"==",index[lang][idx][0],'==',index[lang][idx][1],file=INDEX)
                            total_docs_+=1
                        doc= Counter()
                        total_docs+=1
                    else:
                        if process:
                            doc.update(line2words(line.strip(),sw[lang]))
                verbose("\nTotal number of documents ",lang," ",total_docs_," from ", total_docs) 
     
        verbose("Creating vocabulary ",lang)
        with codecs.open(os.path.join(args.odir,"{0}wiki.voca".format(lang)),'w','utf8') as VOCA:
            for i,(w,n) in enumerate(vocab):
                print(u"{0} = {1} = {2} = {3}".format(w,i+nvoca,n,vocab_doc[lang][w]),file=VOCA)

        nvoca+=len(vocab)

        verbose("Total number of words in vocab",len(vocab))

    
