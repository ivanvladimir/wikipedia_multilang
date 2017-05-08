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
    for lang in args.LANG:
        max_pos=0
        docs={}
        with open(os.path.join(args.idir,"{0}wiki.position.corpus".format(lang))) as FILE:
            for line in FILE:
                line=line.strip()
                bits=line.split(' ',1)
                idx=int(bits[0])
                docs[idx]=bits[1]
                max_pos = max(max_pos,int(idx))
        verbose("Documents recoverd ",lang,": ", len(docs))
        verbose("Maximum position ",lang,": ", max_pos)

        verbose("\nWriting corpus") 
        with open(os.path.join(args.odir,"{0}wiki.corpus".format(lang)),'w') as CORPUS:
            for pos in range(max_pos+1):
                try:
                    info=docs[pos]
                    print(info.strip(),file=CORPUS)
                except KeyError:
                    print(0,file=CORPUS)
                    
     
