----------------------------------
 ImportFromGalaxyAtPasteur Readme
----------------------------------

Bioblend API (http://bioblend.readthedocs.org/) is used 
to extract tool data from a Galaxy instance:
   1/ Installed tool list extraction
   2/ tool metadata extraction


What is included in this directory: 
   1/ Extraction of  all available metadata from tools installed on a galaxy 
   instance (institut pasteur's) for biotool xsd in JSON format.
   	- Examples are now available in the github directory biotools_from_galaxy_at_pasteur
	- the script galaxy_biotool_parser.py enables to parse a galaxy instance and get tools 
	  installed from toolshed (it's the first version, it will be improved)
	  --> requirments: bioblend api available on github (https://github.com/afgane/bioblend.git)

	
	-TIPS:
	 How to use the script:
	 #python galaxy_biotool_parser.py --galaxy_url $GALAXYURL --api_key $APIKEY --tool_dir ../biotools_from_galaxy_at_pasteur
	 Remark: the directory of tool metadata, needs to be created before running the script.

	
	-REMARKS: 
	  1/xml version may not correspond to the tool version 
	  2/

What's next: 

   2/ Json enrichment with EDAM ontologies and other 
extraction data such as "ImportFromGensoftAtPasteur".
(All Galaxy Pasteur tools are included in gensoftAtPasteur)


   3/ Adapt the extraction script for it to be used on any 
galaxy instance.
