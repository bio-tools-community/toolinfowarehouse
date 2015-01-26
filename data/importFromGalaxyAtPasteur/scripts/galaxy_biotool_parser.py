"""
Created on Oct. 23, 2014

@author: Olivia Doppelt-Azeroual, Institut Pasteur, Paris
@contact: olivia.doppelt@pasteur.fr
@project: toolinfowarehouse
@githuborganization: edamontology
"""

import sys
import os
import re
import pprint
import string
import argparse
import json

#to parse owl EDAM file
from rdflib import Graph
#from rdflib.term import URIRef
#from rdflib.resource import Resource
#from rdflib.namespace import RDFS


from bioblend.galaxy.client import ConnectionError
from bioblend.galaxy import GalaxyInstance


def build_tool_name(tool_id):
    """
    @tool_id: tool_id
    builds the tool_name regarding its toolshed id
   """
    print tool_id
    id_list = string.split(tool_id, '/')
    return string.join(id_list[-2:], '_')


def get_source_registry(tool_id):
    try:
    #    tool_id.index('toolshed')
        source = string.split(tool_id, '/')
        for i in range(len(source) - 1):
            if source[i].find('toolshed'):
                return (source[i + 1] + '_' + source[i - 1])
    except ValueError:
        print "ValueError:", tool_id
        return ""


def get_tool_name(tool_id):
    try:
        source = string.split(tool_id, '/')[-2]
        return source
    except ValueError:
        print "ValueError:", tool_id
        return ""


def get_edam_short_id(long_id):
        if long_id is None:
            return None
        return re.sub('http://edamontology.org/([a-zA-Z][a-zA-Z0-9]*)_([0-9]*)',
               'EDAM_\g<1>:\g<2>', long_id)


def build_edam_dict(edam_file):
    # from the owl EDAM file, prints a usable parsing txt file
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






def build_metadata_one(tool_meta_data, url):
    """
      builds general_dict
      @param: tool_meta_data for one tool extracted from galaxy
    """
    gen_dict = {k: tool_meta_data[k] for k in (u'version', u'description')}
    gen_dict[u'name'] = tool_meta_data[u'id']
    gen_dict[u'uses'] = [{"usesName": url,
                          "usesHomepage": url,
                          "usesVersion": gen_dict[u'version']
        }]
    gen_dict[u'collection'] = [url]
    gen_dict[u'sourceRegistry'] = get_source_registry(tool_meta_data[u'id'])
    gen_dict[u'softwareType'] = 'Tool'
    gen_dict[u'maturity'] = [{u'uri': "",
                            u'term': 'production'
                            }]
    gen_dict[u'platform'] = [{u'uri': "",
                              u'term': 'Linux'
                              }]
    # these fields need to be filled with MODULE ressource at Pasteur
    #gen_dict[u'language'] = []
    #gen_dict[u'topic'] = []
    #gen_dict[u'tag'] = []
    #gen_dict[u'licence'] = []
    #gen_dict[u'cost'] = []
    #gen_dict[u'credits'] = []
    #gen_dict[u'docs'] = []

    try:
        # citations are missing from the bioblend show tool
        # need adjustments to consider them once they are
        # included
        gen_dict[u'publications'] = [tool_meta_data[u"citations"]]
    except KeyError:
        pass
        #gen_dict[u'publications'] = []

    return gen_dict


def build_case_inputs(case_dict, input):
    dict_cases = {}
    for inp in input[u'cases']:

        for elem in inp[u'inputs']:
            if elem[u'type'] == u'data':
                if dict_cases.get(inp[u'value']) is None:
                    dict_cases[inp[u'value']] = [elem]
                else:
                    dict_cases[inp[u'value']].append(elem)

                # repeat in conditional

            if elem[u'type'] == u'repeat':
                try:
                    cases = elem[u'inputs'][0][u'cases']

                    for case in cases:
                        if case[u'inputs'] != []:
                            for case_input in case[u'inputs']:
                                if case_input[u'type'] == u'data':
                                    if dict_cases.get(inp[u'value']) is None:
                                        dict_cases[inp[u'value']] = [case_input]
                                    else:
                                        dict_cases[inp[u'value']].append(case_input)

                except KeyError:
#                    print "KeyError key == REPEAT"
                    for el in elem[u'inputs']:
                        if el[u'type'] == u'data':
                            if dict_cases.get(inp[u'value']) is None:
                                dict_cases[inp[u'value']] = [el]
                            else:
                                dict_cases[inp[u'value']].append(el)

    case_dict.update({i: j for i, j in dict_cases.items() if len(j) != 0})


def build_input_for_json(list_inputs):
    liste = []
    inputs = {}
    try:
        try:

            for input in list_inputs:
                inputDict = {}
                inputDict[u'dataType'] = {u'uri': "", u'term': input[u'type']}

                try:
                    formatList = string.split(input[u'format'], ',')
                except AttributeError:
                    formatList = ["AnyFormat"]

                list_format = []
                for format in formatList:
                    dict_format = {u'uri': "", u'term': format}
                    list_format.append(dict_format)
                inputDict[u'dataFormat'] = list_format
                inputDict[u'dataHandle'] = input[u'label']
                liste.append(inputDict)

        except KeyError:
                inputDict[u'dataType'] = {u'uri': "", u'term': input[u'type']}
                formatList = input[u'extensions']
                for format in formatList:
                    inputDict[u'dataFormat'].append({u'uri': "", u'term': format})
                inputDict[u'dataHandle'] = input[u'label']
                liste.append(inputDict)

    except KeyError:
        inputDict[u'dataType'] = {u'uri': "", u'term': input[u'type']}
        inputDict[u'dataFormat'] = []
        inputDict[u'dataHandle'] = input[u'label']
        liste.append(inputDict)

    return liste


def build_fonction_dict(tool_meta_data):
    """
    builds function dict
    2 steps for inputs, get only the data format and
    dict comprehension to keep only important info
    1 steps for outputs, only dict comprehension
    """
    func_dict = {}
    func_list = []
    inputs = {}
    outputs = []
    inputs_fix = []
    dict_cases = {}
    inputs_case = {}

    for input in tool_meta_data[u'inputs']:
        if input[u'type'] == u'data':
            inputs_fix.append(input)
        # repeat not in conditional
        if input[u'type'] == u'repeat':
            for rep in input[u'inputs']:
                if rep[u'type'] == u'data':
                    print 'repeeeeeeaaaaaatttt'
                    inputs_fix.append(rep)
                elif rep[u'type'] == "conditional":
                    build_case_inputs(dict_cases, rep)
        if input[u'type'] == "conditional":
            build_case_inputs(dict_cases, input)

#__________________INPUT DICT _________________________
    if len(dict_cases) == 0:
        inputs["input_fix"] = build_input_for_json(inputs_fix)
    else:
        for key, case in dict_cases.iteritems():
            inputs[key] = build_input_for_json(case) + build_input_for_json(inputs_fix)

#_____________OUTPUT DICT_______________________________________

    for output in tool_meta_data[u'outputs']:
        outputDict = {}
        outputDict[u'dataType'] = []
        outputDict[u'dataFormat'] = {u'uri': "", u'term': output[u'format']}
        outputDict[u'dataHandle'] = output[u'name']
        outputs.append(outputDict)

    if inputs.get("input_fix") is None:
        for input_case_name, item in inputs.items():
            func_dict = {}
            func_dict[u'description'] = tool_meta_data[u'description']
            func_dict[u'functionName'] = []
            func_dict[u'output'] = outputs
            func_dict[u'input'] = item
            func_dict[u'functionHandle'] = 'MainFunction'
            func_dict[u'annot'] = input_case_name
            func_list.append(func_dict)
    else:
        func_dict[u'description'] = tool_meta_data[u'description']
        func_dict[u'functionName'] = []
        func_dict[u'output'] = outputs
        func_dict[u'input'] = inputs[u"input_fix"]
        func_dict[u'functionHandle'] = 'MainFunction'
        func_list.append(func_dict)

    return func_list


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Galaxy instance tool\
        parsing, for integration in biotools/bioregistry")

    parser.add_argument("--galaxy_url", help="url to the analyze \
        galaxy instance")

    parser.add_argument("--api_key", help="galaxy user api key")

    parser.add_argument("--tool_dir", help="directory to store the tool\
        json (needs to be created before running the script")

    parser.add_argument("--collection_name", help="collection name \
        matchine the galaxy url")

    parser.add_argument("--edam_file", help="edam own file to create  \
        the edam_dict")

    args = parser.parse_args()
    gi = GalaxyInstance(args.galaxy_url, key=args.api_key)

    tools = gi.tools.get_tools()
    tools_meta_data = []
    new_dict = {}
    json_ext = '.json'

    edam_dict = {}

    edam_dict = build_edam_dict(args.edam_file)

    for i in tools[0:1]:
        try:
            # improve this part, important to be able to get all tool from any toolshed
            if not i['id'].find("galaxy.web.pasteur.fr") or not i['id'].find("testtoolshed.g2.bx.psu.edu") or not i['id'].find("toolshed.g2.bx.psu.edu"):
                tool_metadata = gi.tools.show_tool(tool_id=i['id'], io_details=True, link_details=True)

                tools_meta_data.append(tool_metadata)
          #  else:
           #     print i['id']
        except ConnectionError:
            print "ConnectionError"
            pass

    for tool in tools_meta_data:
        tool_name = build_tool_name(tool[u'id'])
        try:

            function = build_fonction_dict(tool)
            #print "TYPE FUNCTION:", type(function)
            if len(function) > 1:
                print "THERE WILL BE  " + str(len(function)) + "json"
                for func in function:
                    pprint.pprint(func)
                    #inputs = func[u"input"]
                    name = re.sub("[\.\,\:;\(\)\./]", "_", func[u'annot'], 0, 0)
                    with open(os.path.join(os.getcwd(), args.tool_dir, tool_name + "_"+ name + json_ext), 'w') as tool_file:
                        general_dict = build_metadata_one(tool, args.galaxy_url)
                        general_dict["function"] = func
                        json.dump(general_dict, tool_file, indent=4)
                        tool_file.close()

            else:
                with open(os.path.join(os.getcwd(), args.tool_dir, tool_name + json_ext), 'w') as tool_file:
                    general_dict = build_metadata_one(tool, args.galaxy_url)
                    general_dict["function"] = function[0]
                    json.dump(general_dict, tool_file, indent=4)
                    tool_file.close()


        except SystemExit:
            pass