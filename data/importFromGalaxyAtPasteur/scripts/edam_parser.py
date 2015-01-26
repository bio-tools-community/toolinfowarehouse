"""
Created on Jan. 26, 2015

@author: Olivia Doppelt-Azeroual, Institut Pasteur, Paris
@contact: olivia.doppelt@pasteur.fr
@project: toolinfowarehouse
@githuborganization: edamontology
@inspired by mob_edam_import from mobyle2 project on github

command line:
    python edam_parser.py --edam_file EDAM_1.8.owl


"""


import re
import argparse

#to parse owl EDAM file
from rdflib import Graph


def get_edam_short_id(long_id):
        if long_id is None:
            return None
        return re.sub('http://edamontology.org/([a-zA-Z][a-zA-Z0-9]*)_([0-9]*)',
               'EDAM_\g<1>:\g<2>', long_id)


def build_edam_dict(edam_file):
    # recuperer le label et le EDAM term et construire un dict

    g = Graph().parse(source=edam_file)

    for row in g.query("""
    SELECT ?class ?name
    WHERE {
           ?class rdfs:label ?name
           }
    """):
        namespace = re.sub('http://edamontology.org/([a-zA-Z][a-zA-Z0-9]*)_([0-9]*)', '\g<1>', row[0])

        if namespace in ['data', 'format', 'identifier', 'topic', 'operation']:
            print '{!s}, "{!s}"'.format(get_edam_short_id(row[0]), row[1])
        else:
            continue

    return {}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EDAM OWL PARSER to build a edam_dict")
    parser.add_argument("--edam_file", help="edam own file to create  \
    the edam_dict")

    args = parser.parse_args()
    edam_dict = {}

    edam_dict = build_edam_dict(args.edam_file)




