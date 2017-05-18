#!/bin/bash

# Converts wikipedia text extracted into corpus with positions, vocabularies and index
python python/wikis2corpus.py -v en es pt pl de fr he el ar fa fi cy it ru tk
# Order corpus to be pasted later
python python/order.py -v en fr de it es ru pl pt fa ar fi he el cy tk
# Paste all corpus align by links
python python/paste.py -v en fr de it es ru pl pt fa ar fi he el cy tk
# Conver copurs into ifs
smhcmd ifindex data/fullwiki.corpus data/fullwiki.ifs
