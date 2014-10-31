Conventions for imports from Gensoft, Mobyle, and Galaxy at Pasteur
===================================================================

We import from three different sources of tools hosted at the Institut Pasteur:
* Gensoft: a package manager that is specific to the central scientific 
  resources, and relies on MODULES to manage multiple versions
  of the same tool.
* Galaxy: an online bioinformatics workbench.
* Mobyle: another online bioinformatics workbenches.

All of these resources can be registered in ToolInfoWarehouse. The structure of 
these resource is mapped as follows:
* package of origin: EMBOSS, Phylip, ViennaRNA, etc. as a collection
* source of origin: Gensoft, Galaxy, Mobyle as a collection
* each resource: clustalw, blastall, seqret, etc. as a tool
* each resource is prefixed with its source of origin and its package
  of origin.
* Mobyle and Galaxy resources "use" their Gensoft dependencies

Example: seqret from EMBOSS:
* XML from Gensoft: Gensoft_EMBOSS_6.6.0_seqret.xml,
  "collections" Gensoft and EMBOSS.
* XML from Mobyle: Mobyle_EMBOSS_6.6.0_seqret.xml, 
  "uses" Gensoft_EMBOSS_6.6.0_seqret.xml,
  "collections" Mobyle and EMBOSS.
* XML from Galaxy: Galaxy_EMBOSS_6.6.0_seqret.xml
  "uses" Gensoft_EMBOSS_6.6.0_seqret.xml,
  "collections" Galaxy and EMBOSS.
