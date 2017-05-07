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


function join_by { local d=$1; shift; echo -n "$1"; shift; printf "%s" "${@/#/$d}"; }

function extract {
	LANGS=$*
	for LANG in $LANGS
	do
		echo "Procesing $LANG ..."
		ARGS=()
		for LANG2 in $LANGS
		do
			if [ $LANG != $LANG2 ] 
			then
				ARGS+=($LANG2)
			fi
		done
		EXP=`join_by '\|' ${ARGS[@]}`
		echo "Looking for $EXP ..."
		python python/mysqldump_to_csv.py data/wiki${LANG}.links.sql | grep ",\(${EXP}\)," > data/${LANG}wiki.links.csv
	done
}


mkdir -p data
#extract tk es en pl pt de cy fa fi fr he  it ru  el ar 
extract it fi pl
