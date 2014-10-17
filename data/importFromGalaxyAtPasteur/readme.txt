----------------------------------
 ImportFromGalaxyAtPasteur Readme
----------------------------------

Bioblend API (http://bioblend.readthedocs.org/) is used 
to extract tool data from a Galaxy instance:
   1/ Installed tool list extraction
   2/ tool metadata extraction


What to do: 
   1/ Extract all available information for biotool xsd 
in JSON format.
   	Example for one tool: 


	----------------------------------------
 {u'collectionName': 'GalaxyAtPasteur',
  u'description': u'Soap aligner/soap2',
  u'fonction': {u'description': u'Soap aligner/soap2',
                u'functionHandle': 'MainFunction',
                u'inputs': [{u'format': u'fastq, fasta',
                             u'label': u'Read 1 preprocessed',
                             u'name': u'fqinput',
                             u'type': u'data'}],
                u'outputs': [{u'format': u'text',
                              u'label': u'Soap mapped reads',
                              u'name': u'output'},
                             {u'format': u'fasta',
                              u'label': u'Soap UnMapped reads',
                              u'name': u'unmappedreads'},
                             {u'format': u'text',
                              u'label': u'Soap UnPaired reads',
                              u'name': u'unpairedreads'}]},
  u'id': u'galaxy.web.pasteur.fr/toolshed-pasteur/repos/odoppelt/soap/soapAligner/2.21.1',
  u'maturity': 'production',
  u'name': u'Soap aligner',
  u'platform': 'Linux',
  u'softwareType': 'Tool',
  u'sourceRegistry': u'toolshed-pasteur',
  u'version': u'2.21.1'},
  	 ----------------------------------------



   2/ Json enrichment with EDAM ontologies and other 
extraction data such as "ImportFromGensoftAtPasteur".
(All Galaxy Pasteur tools are included in gensoftAtPasteur)


   3/ Adapt the extraction script for it to be used on any 
galaxy instance.
