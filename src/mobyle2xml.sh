#!/bin/bash
for f in `ls ../data/importFromMobyle1AtPasteur/raw/*.xml`;
    do name=`basename $f`;
    echo processing $name from $f;
    xsltproc -stringparam mobyle_root $1 -stringparam mobyle_contact $2 mobyle2xml.xsl $f | xmllint --format - > ../data/importFromMobyle1AtPasteur/result/$name;
    done
