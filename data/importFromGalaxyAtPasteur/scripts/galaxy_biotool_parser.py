"""
Created on Oct. 23, 2014

@author: Olivia Doppelt-Azeroual
@contact: olivia.doppelt@pasteur.fr
@project: toolinfowarehouse
@organization: edamontology
"""

import sys
import os
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


def get_collection_name(tool_id):
    try:
        source = string.split(tool_id, '/')[0]
        return source
    except ValueError:
        print "ValueError:", tool_id
        return ""


def build_metadata_one(tool_meta_data, url):
    """
      builds general_dict
      @param: tool_meta_data for one tool extracted from galaxy
    """
    gen_dict = {k: tool_meta_data[k] for k in (u'name', u'id',
        u'version', u'description')}
    gen_dict[u'collectionName'] = url
    gen_dict[u'softwareType'] = 'Tool'
    gen_dict[u'sourceRegistry'] = get_source_registry(gen_dict[u'id'])
    gen_dict[u'maturity'] = 'production'
    gen_dict[u'platform'] = 'Linux'
    try:
        gen_dict[u'citations'] = tool_meta_data[u"citations"]
    except KeyError:
        gen_dict[u'citations'] = ""

    return gen_dict


def build_fonction_dict(tool_meta_data):
    """
    builds function dict
    2 steps for inputs, get only the data format and
    dict comprehension to keep only important info
    1 steps for outputs, only dict comprehension
    """
    func_dict = {}
    inputs = []
    outputs = []
    inputs_complete = [elem for elem in tool_meta_data[u'inputs'] if elem[u'type'] in [u'data']]
    try:
        try:
            for input in inputs_complete:
                elem = {i: input[i] for i in (u'format', u'type',
                    u'label', u'name')}
                inputs.append(elem)
        except KeyError:
                elem = {i: input[i] for i in (u'extensions',
                    u'type', u'label', u'name')}
                inputs.append(elem)
    except KeyError:
        elem = {i: input[i] for i in (u'type', u'label', u'name')}
        inputs.append(elem)

    for output in tool_meta_data[u'outputs']:
        outputs.append({o: output[o] for o in (u'format', u'label', u'name')})

    func_dict[u'description'] = tool_meta_data[u'description']
    func_dict[u'outputs'] = outputs
    func_dict[u'inputs'] = inputs
    func_dict[u'functionHandle'] = 'MainFunction'
    return func_dict


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Galaxy instance tool\
        parsing, for integration in biotools/bioregistry")

    parser.add_argument("--galaxy_url", help="url to the analyzed galaxy instance")
    parser.add_argument("--api_key", help="galaxy user api key")
    parser.add_argument("--tool_dir", help="directory to store the tool\
        json (needs to be created before running the script")

    args = parser.parse_args()
    gi = GalaxyInstance(args.galaxy_url, key=args.api_key)

    tools = gi.tools.get_tools()
    tools_meta_data = []
    new_dict = {}
    json_ext = '.json'

    for i in tools[0:10]:
        try:
            # improve this part, important to be able to get all tool from any toolshed ...
            if not i['id'].find("galaxy.web.pasteur.fr") or not i['id'].find("testtoolshed.g2.bx.psu.edu") or not i['id'].find("toolshed.g2.bx.psu.edu"):
                tools_meta_data.append(gi.tools.show_tool(tool_id=i['id'], io_details=True, link_details=True))
            else:
                print i['id']
        except ConnectionError:
            pass

    for tool in tools_meta_data:
        tool_name = build_tool_name(tool[u'id'])
        with open(os.path.join(os.getcwd(), args.tool_dir, tool_name + json_ext), 'w') as tool_file:
            general_dict = build_metadata_one(tool, args.galaxy_url)
            general_dict[u'fonction'] = build_fonction_dict(tool)
            json.dump(general_dict, tool_file, indent=4)
            tool_file.close()
