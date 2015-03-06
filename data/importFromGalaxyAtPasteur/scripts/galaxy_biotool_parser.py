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

from bioblend.galaxy.client import ConnectionError
from bioblend.galaxy import GalaxyInstance


def build_tool_name(tool_id):
    """
    @tool_id: tool_id
    builds the tool_name regarding its toolshed id
   """
    #print tool_id
    id_list = string.split(tool_id, '/')
    return string.join(id_list[-2:], '_')


def get_source_registry(tool_id):
    try:
        source = string.split(tool_id, '/')
        return "https://" + '/'.join(source[0:len(source) - 2])
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


def format_description(description):
    """
    Test the first and last char of a description and replace them
    with the format adapted to Elixir
    """
    try:
        size = len(description)
        if description[size - 1] == '.':
            return description[0].upper() + description[1:size]
        else:
            return description[0].upper() + description[1:size] + '.'
    except IndexError:
        print description


def build_metadata_one(tool_meta_data, url):
    """
      builds general_dict
      @param: tool_meta_data for one tool extracted from galaxy
    """

    if url == "https://galaxyapi.web.pasteur.fr":
        ressourceName = "Galaxy@pasteur"
        homepage = "https://galaxy.web.pasteur.fr"
    else:
        ressourceName = url
        homepage = url
#    gen_dict = {k: tool_meta_data[k] for k in (u'version', u'description')}

    gen_dict = {}
    gen_dict[u'version'] = tool_meta_data[u'version']
    gen_dict[u'description'] = format_description(tool_meta_data[u'description'])
    gen_dict[u'uses'] = [{"usesName": tool_meta_data[u'id'],
                          "usesHomepage": url,
                          "usesVersion": gen_dict[u'version']
        }]
    gen_dict[u'collection'] = ressourceName
    gen_dict[u'sourceRegistry'] = get_source_registry(tool_meta_data[u'id'])
    gen_dict[u'resourceType'] = [{"term": "Tool (analysis)", "uri": "http://www.cbs.dtu.dk/ontology/resource_type/7"}]
    gen_dict[u'maturity'] = [{u'uri': "",
                            u'term': 'production'
                            }]
    gen_dict[u'platform'] = [{u'uri': "",
                              u'term': 'Linux'
                              }]
    gen_dict[u'interface'] = [
        {u'interfaceType': {
            u'term': "WEB UI",
            u'uri': "http://www.cbs.dtu.dk/ontology/interface_type/3"
            }}
        ]
    gen_dict[u'contact'] = {
        u'contactEmail': 'galaxy@pasteur.fr',
        u'contactURL': '',
        u'contactName': 'Institut Pasteur galaxy team',
        u'contactRole': 'Computer Biologist'
        }
    # these fields need to be filled with MODULE ressource at Pasteur
    gen_dict[u'language'] = []
    gen_dict[u'topic'] = [{u'term': "EDAM_topic:0003", u'uri':"http://edamontology.org/topic_0003"}]
    gen_dict[u'tag'] = []
    gen_dict[u'license'] = []
    gen_dict[u'cost'] = []
    gen_dict[u'credits'] = []
    gen_dict[u'docs'] = []
    gen_dict[u'publications'] = []
    gen_dict[u'homepage'] = homepage
    gen_dict[u'accessibility'] = "private"

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


def find_edam_term(edam_name, edam_dict, cond):
    """
    edam_name: term to find in the edam_dict
    edam_dict: edam
    cond: term to not include is found because of edam_name
    """
    edam = ""
    for k, value in edam_dict.items():
        #print value[0], edam_name
        if (re.match(value[0], edam_name, re.IGNORECASE)) is not None and (re.match(r""+cond, k)) is None:
            return(k, value[1])
        else:
            edam = edam_name, "no uri"
    return edam


def build_input_for_json(list_inputs, edam_dict):
    liste = []
    #inputs = {}
    try:
        try:

            for input in list_inputs:
                inputDict = {}
                uri, term = find_edam_term(input[u'type'], edam_dict, "EDAM_format")
                inputDict[u'dataType'] = {u'uri': uri, u'term': term}

                try:
                    formatList = string.split(input[u'format'], ',')
                except AttributeError:
                    formatList = ["AnyFormat"]

                list_format = []
                for format in formatList:
                    term, uri = find_edam_term(format, edam_dict, "EDAM_data")
                    dict_format = {u'uri': uri, u'term': term}
                    list_format.append(dict_format)

                inputDict[u'dataFormat'] = list_format
                inputDict[u'dataHandle'] = input[u'label']
                liste.append(inputDict)
                #pprint.pprint(inputDict)

        except KeyError:
                uri, term = find_edam_term(input[u'type'], edam_dict, "EDAM_format")
                inputDict[u'dataType'] = {u'uri': uri, u'term': term}
                formatList = input[u'extensions']
                for format in formatList:
                    term, uri = find_edam_term(format, edam_dict, "EDAM_data")
                    inputDict[u'dataFormat'].append({u'uri': uri, u'term': term})
                inputDict[u'dataHandle'] = input[u'label']
                liste.append(inputDict)

    except KeyError:
        term, uri = find_edam_term(input[u'type'], edam_dict, "EDAM_format")
        inputDict[u'dataType'] = {u'uri': uri, u'term': term}
        inputDict[u'dataFormat'] = []
        inputDict[u'dataHandle'] = input[u'label']
        liste.append(inputDict)

    return liste


def build_fonction_dict(tool_meta_data, edam_dict):
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
                    inputs_fix.append(rep)
                elif rep[u'type'] == "conditional":
                    build_case_inputs(dict_cases, rep)
        if input[u'type'] == "conditional":
            build_case_inputs(dict_cases, input)

#__________________INPUT DICT _________________________
    if len(dict_cases) == 0:
        inputs["input_fix"] = build_input_for_json(inputs_fix, edam_dict)
    else:
        for key, case in dict_cases.iteritems():
            inputs[key] = build_input_for_json(case, edam_dict) + build_input_for_json(inputs_fix, edam_dict)

#_____________OUTPUT DICT_______________________________________

    for output in tool_meta_data[u'outputs']:
        outputDict = {}
        term, uri = find_edam_term("data", edam_dict, "EDAM_format")
        outputDict[u'dataType'] = {u'uri': uri, u'term': term}
        term, uri = find_edam_term(output[u'format'], edam_dict, "EDAM_data")
        outputDict[u'dataFormat'] = {u'uri': uri, u'term': term}
        #print output[u'format']
        outputDict[u'dataHandle'] = output[u'name']
        outputs.append(outputDict)

    if inputs.get("input_fix") is None:
        for input_case_name, item in inputs.items():
            func_dict = {}
            func_dict[u'description'] = format_description(tool_meta_data[u'description'])
            func_dict[u'functionName'] = [{"uri":"http://edamontology.org/operation_0004"}]
            func_dict[u'output'] = outputs
            func_dict[u'input'] = item
            func_dict[u'functionHandle'] = input_case_name
            #func_dict[u'annot'] = input_case_name
            func_list.append(func_dict)
    else:
        func_dict[u'description'] = format_description(tool_meta_data[u'description'])
        func_dict[u'functionName'] = []
        func_dict[u'output'] = outputs
        func_dict[u'input'] = inputs[u"input_fix"]
        func_dict[u'functionHandle'] = 'MainFunction'
        func_list.append(func_dict)
    #pprint.pprint(func_list)
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

    parser.add_argument('--login', help="registry login")

    args = parser.parse_args()
    gi = GalaxyInstance(args.galaxy_url, key=args.api_key)

    tools = gi.tools.get_tools()

    tools_meta_data = []
    new_dict = {}
    json_ext = '.json'

    # Building of the EDAM_DICT DATA
    # Ne mettre que les data et les formats dans le dict pour optimiser
    edam_dict = {}
    with open(args.edam_file, 'r') as f:
        for line in f:
            split_line = string.split(line, '#@#')
            if (re.match(r"EDAM_topic", split_line[0])) is None and (re.match(r"EDAM_operation", split_line[0])) is None:
                if split_line[1].rstrip('\n') == "TSV":
                    edam_dict[split_line[0]] = ["tabular", split_line[2].rstrip('\n')]
                else:
                    edam_dict[split_line[0]] = [split_line[1], split_line[2].rstrip('\n')]
    f.closed

    for i in tools:
        try:
            # improve this part, important to be able to get all tool from any toolshed
            if not i['id'].find("galaxy.web.pasteur.fr") or not i['id'].find("testtoolshed.g2.bx.psu.edu") or not i['id'].find("toolshed.g2.bx.psu.edu"):
                tool_metadata = gi.tools.show_tool(tool_id=i['id'], io_details=True, link_details=True)
                #pprint.pprint(tool_metadata)
                tools_meta_data.append(tool_metadata)
          #  else:
           #     print i['id']
        except ConnectionError:
            print "ConnectionError"
            pass

    for tool in tools_meta_data:
        tool_name = build_tool_name(tool[u'id'])
        try:

            function = build_fonction_dict(tool, edam_dict)
            #print "TYPE FUNCTION:", type(function)
            with open(os.path.join(os.getcwd(), args.tool_dir, tool_name + json_ext), 'w') as tool_file:
                general_dict = build_metadata_one(tool, args.galaxy_url)
                general_dict[u"function"] = function
                general_dict[u"name"] = get_tool_name(tool[u'id'])
                json.dump(general_dict, tool_file, indent=4)

        except SystemExit:
            pass
