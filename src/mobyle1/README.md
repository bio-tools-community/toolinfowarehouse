Launch the Mobyle1 import script:
./mobyle2xml.sh 'http://mobyle.pasteur.fr' 'mobyle@pasteur.fr'
Validate produced XML:
xmllint --noout --schema biotools-beta06.xsd ../data/importFromMobyle1AtPasteur/result/*.xml 2>&1| grep 'validity error'
