#!/bin/bash
sid="${1}"
if test -z ${sid} ; then
	echo "ID (without the S) required" 1>&2
	exit 1
fi
if test -f "S${sid}.xml" ; then
	echo "S${sid}.xml exists" 1>&2
	exit 0
fi
url='https://www.treebase.org/treebase-web/search/study/summary.html?id='"${sid}"
echo "Trying from ${url} ..." 1>&2
if ! curl -f -L "${url}" > .scratch.xml 2>/dev/null ; then
	echo "Could not fetch study S${sid}.xml from ${url}" 1>&2
	rm -f .scratch.xml
	exit 1
else
	echo ${sid}
fi
