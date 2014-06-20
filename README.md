toolinfowarehouse
=================
This project aims at importing and consolidating bioinformatics tool descriptions from a number of tools metadata resources, so that they can be synchronised with tools registries, catalogues, or integrated frameworks (primarily the global generic BMB/ELIXIR tools registry). The resources in focus of this pilot attempt may include:
- mobyle
- gensoft
- emboss
- galaxy
- seqwiki
- debian-med
- and sooner or later also the global generic tools registry developed with the support from BioMedBridges and ELIXIR.

We aim at attempting to integrate primarily two very distinct kinds of tools information:
- EDAM annotation [EMBOSS, SEQwiki, Gensoft/BioWeb2, Mobyle2, at some point also Debian Med]
- detailed interface and version information [Mobyle, Galaxy, EMBOSS]

But in addition, we aim at integrating *ALL* metadata available in the imported resource, so that no information is lost. We should only remove the "sensitive" site-specific metadata such as the server, filesystem, or user details. Example metadata that certainly is of interest includes:
- contacts, credits, licences, descriptions [all]
- one future day hopefully also the technical and scientific dependencies [Debian Med]



