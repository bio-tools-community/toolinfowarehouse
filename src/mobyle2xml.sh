#!/bin/bash
for f in $1;
    do name=`basename $f`;
    echo processing $name from $f;
    xsltproc mobyle2xml.xsl $f | xmllint --format - > ../data/importFromMobyle1AtPasteur/$name;
    done
