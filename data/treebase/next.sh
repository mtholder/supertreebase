#!/bin/bash
n=`cat .next_id.txt` 
echo $n
if test $n -gt 0 ; then
	bash ../../script/download_or_categorize.bash $n # 2>/dev/null
	nn=`expr $n - 1`
	echo $nn >.next_id.txt
else
	echo Done
	exit 1
fi

