#!/usr/bin/env python 

"""
Created on Feb.2nd , 2015

@author: Eric Deveaud, Institut Pasteur, Paris
@contact: edeveaud@pasteur.fr
@project: toolinfowarehouse
@githuborganization: edamontology

a quick and dirty tool to convert BIODOCS (internal gensoft documentation) to
json suitable for elixir-registry.cbs.dtu.dk

"""


import argparse
import json
import os
import sys

from BiodocParser import *

# tweak modulecmd in order to use 3.3.a updated (not yet released)
os.environ['MODULESHOME'] = ''
os.environ['PY_MODULECMD'] = '/local/gensoft2/adm/Modules/3.3.a/bin/modulecmd'
import module as m

import module as m

INDENT=4

EDAM_URI = "http://edamontology.org"
GENSOFT_MAINTAINER='gensoft@pasteur.fr'
OLIVIAS_UNIQUE_SEPARATOR = '#@#'

DEFAULT_TOPIC=3
DEFAULT_OPERATION=4

FATAL= 1
WARN= 0

def error(exit_val, *msg):
    head=['Warning', 'Error']
    print >> sys.stderr, "%s: %s" % (head[exit_val], " - ".join(map(str, msg)))
    if exit_val:
        sys.exit(exit_val)
    return None


def ontology_parser(fh):
    onto = {}
    for line in fh:
        line=line.strip()
        edam_id, desc, edam_uri = line.split(OLIVIAS_UNIQUE_SEPARATOR)
        kind, edam_number = edam_id.split(':')
        k = int(edam_number)
        onto[k] = { 'id': edam_id
                  , 'desc' : desc
                  , 'kind' : kind
                  , 'uri' : edam_uri
                  }
    return onto


def gensoft_categories2EDAM(term,ontology):
    # gensoft format: EDAM-0002241 --> convert to int
    _, key = term.split('-') 
    key = int(key)
    if key not in ontology: 
        return None
    return  ontology[key]
 
def get_biodocs_contact(biodoc_descriptor):
    return [ { "contactEmail": GENSOFT_MAINTAINER
             , "contactURL": ''
             , "contactName": ''
             , "contactTel": ''
             , "contactRole": "Technical"
             }
            ]

def get_biodocs_interface(biodoc_descriptor):
 return [
         { "interfaceType": { "term": "Command line",
           "uri": "http://www.cbs.dtu.dk/ontology/interface_type/5" }
         }
        ]

def get_biodocs_name(biodoc_descriptor):
    return biodoc_descriptor['NAME']


def get_biodocs_homepage(biodoc_descriptor):
    return biodoc_descriptor['HOME'] if biodoc_descriptor['HOME'] else None


def get_biodocs_description(biodoc_descriptor):
    return ' '.join(biodoc_descriptor['DESCRIPTION'])


def get_biodocs_authors(biodoc_descriptor):
    # as authors are not documented with this granularity in 
    # biodocs, we set up all the authors to contributors.
    return {"creditsContributor": biodoc_descriptor['AUTHORS']}


def get_module_docs(package, version):
    # return biodoc_descriptor['HTMLDOCS'] + biodoc_descriptor['MANPAGES']
    def get_docs(info):
        '''
        get local documentation available for given package
        returns a tuple (htmldocs, txtdocs) of list as str
        '''
        htmldocs = []
        txtdocs = []
        keep = False
        for elem in infos:
            elem = elem.strip()
            if not elem:
                continue
            if elem == "local documentation available:":
                keep = True
                continue
            elif elem == "package provides following commands:":
                break
            if keep:
                if 'bioweb2' in elem:
                    htmldocs.append(elem)
                else:
                    txtdocs.append(elem)
        return htmldocs, txtdocs 

    module= "%s/%s" % (package, version)
    try:
        infos=m.modulehelp(package).split('\n')
    except RuntimeError as err:
        error(FATAL, "module Error", err)

    return get_docs(infos)[0]    
    


def get_biodocs_topics(biodoc_descriptor, ontology_desc):
    topics = []
    for cat in biodoc_descriptor['CATEGORIES']:
        edam=gensoft_categories2EDAM(cat, ontology_desc)
        if edam is None:
            error(WARN, cat, 'unknonw category')
            continue
        if edam['kind'] != 'EDAM_topic':
            continue
        res={ 'term': edam['id']
            , 'uri' : edam['uri']
            }
        topics.append(res)
    if not topics:
        default = ontology_desc[DEFAULT_TOPIC]
        res={ 'term': default['id']
            , 'uri' : default['uri']
            }
        topics.append(res)
    return topics

def get_biodocs_functions(biodoc_descriptor, ontology_desc):
    functions = []
    for cat in biodoc_descriptor['CATEGORIES']:
        edam=gensoft_categories2EDAM(cat, ontology_desc)
        if edam is None:
            error(WARN, cat, 'unknonw category')
            continue
        if edam['kind'] != 'EDAM_operation':
            continue
        res={ 'functionName': [ {'term': edam['id']
                                , 'uri' : edam['uri']
                                }
                              ]
            }
        functions.append(res)
    if not functions:
        default = ontology_desc[DEFAULT_OPERATION]
        res={ 'term': default['id']
            , 'uri' : default['uri']
            }
        functions.append(res)
    return functions
    
def get_biodocs_publications(biodoc_descriptor):
    publications=[publi for publi in biodoc_descriptor['REF'] if publi ]
    refs = []
    for publi in publications:
        _, pub_id = get_doi(publi)
        if pub_id is None: continue
        fields = pub_id.split(':')
        qualifier = fields[0]
        if qualifier.lower() != 'doi':
            continue
        pub_id = ":".join(fields[1:])
        refs.append(pub_id.strip())
    publis = {}
    if refs:
        publis = {'publicationsPrimaryID': refs[0] if refs else []
                 ,'publicationsOtherID': refs[1:]
                 }
    return publis


def get_biodoc_ressource(biodoc_descriptor):
    return [ { "term": "Suite" } ]

def get_biodocs_versions(biodocs):
    return [elem.replace('(default)', '') for elem in biodocs['VERSION']]

def to_document(biodocs):
    if biodocs['PRIVATE']:
        return False
    if biodocs['LIBRARY']:
        return False
    if not biodocs['HOME']:
        return False
    return True

def jason_generator(biodocs, outdir):

    pack_name = get_biodocs_name(biodocs)

    #---- check if worth the documentation
    if not to_document(biodocs):
        error(WARN, pack_name, 'not documented')
        return

    res = {}
    #---- tag with gensoft origin
    res['affiliation'] = "Gensoft @Institut Pasteur"

    #---- common information to all packages version available in 
    #---- gensoft BIODOCS
    #---- mandatory info 
    res['name'] = pack_name
    res['homepage'] = get_biodocs_homepage(biodocs)
    res['resourceType'] = get_biodoc_ressource(biodocs)
    res['interface'] = get_biodocs_interface(biodocs)
    res['description'] = get_biodocs_description(biodocs)
    res['topic'] = get_biodocs_topics(biodocs, onto)
    res['function'] = get_biodocs_functions(biodocs, onto)
    res['contact'] = get_biodocs_contact(biodocs)
    
    #---- accessory info
    publication = get_biodocs_publications(biodocs)
    if publication:
        res['publications'] = publication
    credits = get_biodocs_authors(biodocs)
    if credits:
        res['credits'] = credits

    versions = get_biodocs_versions(biodocs)
    for version in versions:
        res['version'] = version
        # bidocs docs description is broken, no versionnig.
        # so superseed it with the one grabbed from module
        res['docs'] = get_module_docs(pack_name, version)
        
        outfile = "%s_%s.json" %(pack_name, version)
        outfile = os.path.join(outdir, outfile)
        print "dump to %s" %(outfile) 
        try:
            outfh= open(outfile, 'w')
        except IOError as msg:
            error(FATAL, outfile, msg)
        
        json.dump(res, outfh, indent=INDENT)
        outfh.close()
        



if __name__ == '__main__':


    #---- get command line
    parser = argparse.ArgumentParser(description='Biodocs to EDAM registry conversion tool.')
    parser.add_argument('-e', '-edam_ontology', action="store"
                        , type=str
                        , default=None
                        , dest='ONTO'
                        , help='EDAM ontology description file .')
    parser.add_argument('-o', '-out-dir', action="store"
                        , type=str
                        , default='json'
                        , dest='OUTDIR'
                        , help='json outdir.')
    parser.add_argument('args', nargs='*')
    cmdline = parser.parse_args()

    ontology_file = cmdline.ONTO
    outdir = cmdline.OUTDIR

    if ontology_file is None:
        error(FATAL, "missing ontology description: abort")
    with open(ontology_file, 'r') as fh:
        onto = ontology_parser(fh)
    for biodoc_file in cmdline.args:
        with open(biodoc_file, 'r') as fh:
            biodocs = Parser(fh)[0]
            jason_generator(biodocs, outdir)
