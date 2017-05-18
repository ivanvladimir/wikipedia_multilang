#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Consults documents
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
from collections import Counter


if __name__ == "__main__":
    # Command line options
    p = argparse.ArgumentParser("Constults documents")
    p.add_argument("-v", "--verbose",
        action="store_true", dest="verbose", default=False,
        help="Verbose mode")
    p.add_argument("JSON",default=None,
        action="store", help="JSON with topics")
    p.add_argument("WORDS",nargs="+",type=str,
            help="Wikipedia language code")
    args = p.parse_args()

    # prepara función de verbose
    if args.verbose:
        def verbose(*args):
            print(*args)
    else:   
        verbose = lambda *a: None 


    with open(args.JSON) as JSON:
        topics = json.load(JSON)

        for word in args.WORDS:
            for topic in topics:
                if word in [w['Word'] for w in topic['words']]:
                    print(10*"===")
                    print("Topic ",topic['id'],)
                    print("Size",len(topic['words']))
                    langs=Counter([w['Language'] for w in topic['words'] ])
                    print("Languajges",u", ".join([u"{0}({1})".format(k,v) for k,v in langs.most_common()]),len(langs))
                    print("Head (20)",u", ".join([u"{Word}({Language})".format(**w) for w in topic['words'][:20]]))

