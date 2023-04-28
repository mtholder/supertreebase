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
url="https://treebase.org/treebase-web/phylows/study/TB2:S${sid}?format=nexml"
echo "Trying from ${url} ..." 1>&2
if ! curl -f -L "${url}" > .scratch.xml 2>/dev/null ; then
	echo "Could not fetch study S${sid}.xml from ${url}" 1>&2
	rm -f .scratch.xml
	exit 1
fi
if grep 'Sorry! your action is not authorized.' .scratch.xml >/dev/null ; then
	echo "S${sid}.xml is unreleased" 1>&2
	rm -f .scratch.xml
	exit 1
fi
echo "${url}" > "S${sid}.url"
mv .scratch.xml "S${sid}.xml"
echo "S${sid}.xml created" 1>&2