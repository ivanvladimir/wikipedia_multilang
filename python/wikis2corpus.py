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
random.seed()

from collections import Counter,defaultdict
punct=re.compile("\w+", re.UNICODE)

def line2words(line,sws):
    return [w for w in punct.findall(line.lower()) 
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
        action="store", dest="min_per_doc", type=int,default=50,
        help="Minimum words per document [50]")
    p.add_argument("--cutoff",
        action="store", dest="cutoff", type=int,default=10,
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
    indices={}
    indices_docs={}
    title_docs={}
    verbose("Reading documents with links")
    for lang in args.LANG:
        title_docs[lang]=set()
        indices_docs[lang]=set()

    for lang in args.LANG:
        #indices[lang]=defaultdict(lambda : defaultdict(str))
        with open(os.path.join(args.idir,"{0}wiki.links.csv".format(lang))) as FILE:
            for line in FILE:
                bits=line.split(',')
                indices_docs[lang].add(int(bits[0]))
                #indices[lang][bits[1]][int(bits[0])]=bits[2]
                title_docs[bits[1]].add(bits[2])
        verbose("Documents with links in ",lang," ",len(indices_docs[lang]))

    
    verbose("Documents link to")
    for lang in args.LANG:
        verbose("Linked documents in ",lang," ",len(title_docs[lang]))

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

    sys.exit()
    # Extrayendo los vocabularios
    re_header = re.compile('<doc id="(\d+)" url="(w+)" title="(w+)"')
    for lang in args.lang:
        corpus[lang]=Counter()
        vocab_doc[lang]=Counter()
        doc[lang]=Counter()
    idx=[]
    
    
    verbose("Extracting articles")
    for line in codecs.open(opts.WIKI,encoding="utf-8"):
        if re_header.match(line):
            if opts.max and len(idx)==opts.max:
                break
            if not len(idx)%1000:
                print('.',end="")
            corpus.update(doc)
            vocab_doc.update(doc.keys())
            doc= Counter()
            idx.append(line[2:-2].strip())
            doc.update(line2words(line[2:-2].strip(),[]))
        else:
            doc.update(line2words(line.strip(),sws))
    corpus.update(doc)
  
    verbose("Total number of documents",len(idx)) 
    verbose("Vocabulary size",len(corpus)) 
    verbose("Total number of words",sum(corpus.values())) 


    sys.exit()

    files=[]
    indixes=[]
    # Creating splits
    first_split=None
    verbose("Creating splits")
    if len(opts.splits)>0:
        if not sum([float(y) for x,y in opts.splits ]) == 100.0:
            p.error("Split options defined but it does not adds to 100%")
        random.shuffle(idx)
        splits=[]
        ini=0
        first_split=opts.splits[0][0]
        for x,y in opts.splits:
            y=int(y)
            files.append(codecs.open(os.path.join(opts.odir,opts.corpus+"."+x+".corpus"),'w',encoding='utf-8'))
            indixes.append(codecs.open(os.path.join(opts.odir,opts.corpus+"."+x+".index"),'w',encoding='utf-8'))
            splits.append(dict([ (title,(files[-1],x,indixes[-1])) for title in idx[ini:ini+int(y*0.01*len(idx))]]))
            ini+=int(y*0.01*len(idx))
        splits.append(dict([ (title,(files[-1],x,indixes[-1])) for title in idx[ini:]]))
    else:
        files.append(codecs.open(os.path.join(opts.odir,opts.corpus+".corpus"),'w',encoding='utf-8'))
        indixes.append(codecs.open(os.path.join(opts.odir,opts.corpus+".index"),'w',encoding="utf-8"))
        first_split=""
        splits=[dict([(title,(files[-1],"",indixes[-1])) for title in idx])]

    splits_={}
    for split in splits:
        splits_.update(split)
    splits=splits_


    # Extracting voca first split
    vocab=Counter()
    header=None
    ii=0
    if len(opts.splits)<=1:
        vocab=corpus
        vocab_doc=vocab_doc
    else:
        vocab_doc=Counter()
        for line in codecs.open(opts.WIKI,encoding="utf-8"):
            if re_header.match(line):
                if opts.max and ii==opts.max:
                    break

                if not ii%1000:
                    print('.',end="")
 
                header=line[2:-2].strip()
                if splits[header][1]==first_split:
                    vocab.update(doc)
                    vocab_doc=update(doc.keys())
                    doc.update(line2words(header,[]))
                doc= Counter()
                ii+=1
            else:
                if splits[header][1]==first_split:
                    doc.update(line2words(line.strip(),sws))
        if splits[header][1]==first_split:
            vocab.update(doc)

    verbose("Total number of words in vocab",sum(vocab.values()))
    verbose("Total number of words new words per document",sum(vocab_doc.values()))
    vocab=[(w,n) for (w,n) in vocab.most_common() 
            if n>=opts.cutoff and
               (opts.min_per_doc==0 or vocab_doc[w]>=opts.min_per_doc)]
    vocab_={}
    for (i,(w,n)) in enumerate(vocab):
        vocab_[w]=i


    ii=0
    ndocs=0
    header=None
    verbose("Creating corpus")
    for line in codecs.open(opts.WIKI,encoding="utf-8"):
        if re_header.match(line):
            if opts.max and ii==opts.max:
                break
            if not ii%1000:
                print('.',end="")
            if header:
                info=["{0}:{1}".format(vocab_[w],n) for w,n in doc.most_common() if vocab_.has_key(w)] 
                print(len(info)," ".join(info),file=splits[header][0])
                print(ndocs,line.strip(),file=splits[header][2])
                ndocs+=1
            doc= Counter()
            ii+=1
            header=line[2:-2].strip()
            doc.update(line2words(header,[]))
        else:
            doc.update(line2words(line.strip(),sws))
    if header:
        info=["{0}:{1}".format(vocab_[w],n) for w,n in doc.most_common() if vocab_.has_key(w)] 
        print(len(info)," ".join(info),file=splits[header][0])
        print(ndocs,line.strip(),file=splits[header][2])

    for file in files:
        file.close()
    for file in indixes:
        file.close()
 
    verbose("Creating vocabulary")
    vocabf=codecs.open(os.path.join(opts.odir,opts.corpus+".vocab"),"w",encoding='utf-8')
    for i,(w,n) in enumerate(vocab):
        print(u"{0} = {1} = {2} = {3}".format(w,i,n,vocab_doc[w]),file=vocabf)
    vocabf.close()

