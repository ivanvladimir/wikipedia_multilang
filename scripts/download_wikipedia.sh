#!/bin/bash

function check {
	ANS='yes'
	echo $1
	if [ -f $1 ]; then
		read -r -p "${1} exists, $2? [y/N] " response
		if [[ $response =~ ^([yY][eE][sS]|[yY])$ ]]
		then
			ANS='yes'
		else
			ANS='no'
		fi
	fi
}


function download {
	LANG=$1
	DATE=$2
	check data/${LANG}wiki.page.sql.gz "should i download again"
	if [ "$ANS" == "yes" ]; then
		wget -O data/${LANG}wiki.page.sql.gz https://dumps.wikimedia.org/${LANG}wiki/${DATE}/${LANG}wiki-${DATE}-page.sql.gz
		gunzip -c data/${LANG}wiki.page.sql.gz > data/${LANG}wiki.page.sql
	fi

	check data/${LANG}wiki.links.gz  "should i download again"
	if [ "$ANS" == "yes" ]; then
		wget -O data/${LANG}wiki.links.gz https://dumps.wikimedia.org/${LANG}wiki/${DATE}/${LANG}wiki-${DATE}-langlinks.sql.gz
		gunzip -c data/${LANG}wiki.links.gz > data/${LANG}wiki.links.sql
	fi

	check data/${LANG}wiki.articles.bz2 "should i download again"
	if [ "$ANS" == "yes" ]; then
		wget -O data/${LANG}wiki.articles.bz2 https://dumps.wikimedia.org/${LANG}wiki/${DATE}/${LANG}wiki-${DATE}-pages-articles.xml.bz2
	fi

	check data/${LANG}wiki.xml
	if [ "$ANS" == "yes" ]; then
		mkdir extracted
		python python/WikiExtractor.py --no-templates  -cb 1M -o extracted  data/${LANG}wiki.articles.bz2
		find extracted -name '*.bz2' -exec bzip2 -d -c {} \; > data/${LANG}wiki.xml
		rm -rf extracted
	fi
}


mkdir -p data
#download tk 20170420
download es 20170420
download en 20170420
download pl 20170420
download pt 20170420
download de 20170420
download cy 20170420
download fa 20170420
download fi 20170420
download fr 20170420
download he 20170420
download it 20170420
download ru 20170420
download el 20170420
download ar 20170420
