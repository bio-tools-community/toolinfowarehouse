from lxml import etree
import json
import argparse
import requests
import os.path
import getpass

ns = {'btr':'http://biotoolsregistry.org'}

def xfirst(el, path):
    res = el.xpath(path, namespaces=ns)
    return res[0] if res else None

def doc_to_dict(doc):
    for resource_el in doc.getroot().xpath('btr:resource', namespaces=ns):
        resource = {}
        resource['name'] = xfirst(resource_el, 'btr:name/text()')
        resource['homepage'] = xfirst(resource_el, 'btr:homepage/text()')
        resource['version'] = xfirst(resource_el, 'btr:version/text()')
        resource['collection'] = [xfirst(resource_el, 'btr:collection/text()')]
        resource['interface'] = [{'interfaceType': {'term': "WEB UI", 'uri': "http://www.cbs.dtu.dk/ontology/interface_type/3"}}]
        resource['description'] = xfirst(resource_el, 'btr:description/text()')
        resource['topic'] = []
        for topic_el in resource_el.xpath('btr:topic', namespaces=ns):
            term = {}
            if topic_el.xpath('@uri', namespaces=ns):
                term['uri'] = xfirst(topic_el, '@uri')
            if topic_el.xpath('text()'):
                term['term'] = xfirst(topic_el, 'text()')
            resource['topic'].append(term)
        for el in resource_el.xpath('btr:resourceType', namespaces=ns):
            term = {}
            if el.xpath('@uri', namespaces=ns):
                term['uri'] = xfirst(el, '@uri')
            if el.xpath('text()'):
                term['term'] = xfirst(el, 'text()')
            # FIXME all tools are not analysis tools...
            resource['resourceType'] = [{"term": "Tool (analysis)", "uri": "http://www.cbs.dtu.dk/ontology/resource_type/7"}]
        resource['function'] = []
        for function_el in resource_el.xpath('btr:function', namespaces=ns):
            function = {}
            functionName = []
            for term_el in function_el.xpath('btr:functionName', namespaces=ns):
                term = {}
                if term_el.xpath('@uri', namespaces=ns):
                    term['uri'] = xfirst(term_el, '@uri')
                if term_el.xpath('text()'):
                    term['term'] = xfirst(term_el, 'text()')
                functionName.append(term)
            function['functionName'] = functionName
            function['input'] = []
            for input_el in function_el.xpath('btr:input', namespaces=ns):
                _input = {}
                _input['dataHandle'] = xfirst(input_el, 'btr:dataHandle/text()')
                for term_el in input_el.xpath('btr:dataType', namespaces=ns):
                    term = {}
                    if term_el.xpath('@uri', namespaces=ns):
                        term['uri'] = xfirst(term_el, '@uri')
                    if term_el.xpath('text()'):
                        term['term'] = xfirst(term_el, 'text()')
                    _input['dataType'] = term
                _input['dataFormat'] = [] 
                for term_el in input_el.xpath('btr:dataFormat', namespaces=ns):
                    term = {}
                    if term_el.xpath('@uri', namespaces=ns):
                        term['uri'] = xfirst(term_el, '@uri')
                    if term_el.xpath('text()'):
                        term['term'] = xfirst(term_el, 'text()')
                    _input['dataFormat'].append(term)
                function['input'].append(_input)
            function['output'] = []
            for input_el in function_el.xpath('btr:output', namespaces=ns):
                _input = {}
                _input['dataHandle'] = xfirst(input_el, 'btr:dataHandle/text()')
                for term_el in input_el.xpath('btr:dataType', namespaces=ns):
                    term = {}
                    if term_el.xpath('@uri', namespaces=ns):
                        term['uri'] = xfirst(term_el, '@uri')
                    if term_el.xpath('text()'):
                        term['term'] = xfirst(term_el, 'text()')
                    _input['dataType'] = term
                _input['dataFormat'] = [] 
                for term_el in input_el.xpath('btr:dataFormat', namespaces=ns):
                    term = {}
                    if term_el.xpath('@uri', namespaces=ns):
                        term['uri'] = xfirst(term_el, '@uri')
                    if term_el.xpath('text()'):
                        term['term'] = xfirst(term_el, 'text()')
                    _input['dataFormat'].append(term)
                function['output'].append(_input)
            resource['function'].append(function)
        return resource

def auth(login):
    print login
    password = getpass.getpass()
    resp = requests.post('http://elixir-registry.cbs.dtu.dk/api/auth/login','{"username": "%s","password": "%s"}' % (login, password), headers={'Accept':'application/json', 'Content-type':'application/json'}).text
    print resp
    return json.loads(resp)['token']

if __name__ == '__main__':
    # 1. Import XML files from a Mobyle server or from a folder containing XML files
    # 2. Convert to BTR XML
    # 3. Convert to BTR JSON
    # 4. Register to Elixir BTR
    parser = argparse.ArgumentParser(
                 description='Transform Mobyle1 XML to BTR XML and JSON')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--from_server', help="Mobyle server URI to import definitions from")
    group.add_argument('--from_files', help="Mobyle XML files to import definitions from", nargs='+')
    parser.add_argument('--json_dir', help="target directory for JSON files")
    parser.add_argument('--xml_dir', help="target directory for XML files")
    parser.add_argument('--login', help="registry login")
    args = parser.parse_args()
    if args.from_files:
        filenames = args.from_files
    elif args.from_server:
        resp = requests.get(args.from_server+'/net_services.py')
        services = json.loads(resp.text)
        filenames = []
        for key, value in json.loads(resp.text).items():
            filenames.append(value['url'])
    xslt_doc = etree.parse('mobyle2xml.xsl')
    transform = etree.XSLT(xslt_doc)
    params = {'mobyle_root':"'http://mobyle.pasteur.fr'",
              'mobyle_contact':"'mobyle@pasteur.fr'"}
    if args.login:
        print "authenticated"
        token = auth(args.login)
        ok_cnt = 0
        ko_cnt = 0
    for filename in filenames:
        print "processing %s..." % filename
        mobyle_doc = etree.parse(filename)
        xml = transform(mobyle_doc, **params)
        btr_doc = xml
        res = doc_to_dict(btr_doc)
        resource_name = res['name']
        if args.xml_dir:
            xml_path = os.path.join(args.xml_dir, resource_name + '.xml')
            o_file =  open(xml_path, 'w')
            o_file.write(etree.tostring(xml, pretty_print=True))
            o_file.close()
        if args.json_dir:
            json_path = os.path.join(args.json_dir, resource_name + '.json')
            json.dump(res, open(json_path, 'w'), indent=True)
        if args.login and args:
            resp = requests.post('http://elixir-registry.cbs.dtu.dk/api/tool', json.dumps(res), headers={'Accept':'application/json', 'Content-type':'application/json', 'Authorization': 'Token %s' % token})
            #print resp.status_code
            if resp.status_code==201:
                print "%s ok" % resource_name
                ok_cnt += 1
            else:
                print "%s ko, error: %s" % (resource_name, resp.text)
                ko_cnt += 1
    if args.login:
        print "import finished, ok=%s, ko=%s" % (ok_cnt, ko_cnt)
