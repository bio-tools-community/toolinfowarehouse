#! /mount/biotools/bin/python2.7

import sys
import argparse
import json
import os
import os.path

# tweak modulecmd in order to use 3.3.a updated (not yet released)
os.environ['PY_MODULECMD'] = '/local/gensoft2/adm/Modules/3.3.a/bin/modulecmd'
import module_env as m


#print ">>>>>> using: modulecmd %s\n" % (m.getmoduleversion())


#---------- HUGLY SCRIPT TO EXTRACT INFOS FROM MODULE HELP  ----------
#---------- AND GENSOFT BIODOCS                             ----------


#---- some global variables

DEST='/pasteur/homes/edeveaud/Work/EDAM/res'
INST='/local/gensoft2/inst'
MODPATH='/local/gensoft2/modules'
INDENT=4


def error_fatal(*msg):
    print >> sys.stderr, "Error:: %s" % (" - ".join(map(str, msg)))
    sys.exit(1)

def error_warn(*msg):
    print >> sys.stderr, "Warning:: %s" % (" - ".join(map(str, msg)))

def log(*msg):
    if VERBOSE:
        print >> LOGFH, "%s" %(' '.join(map(str, msg)))


def get_edam(modname):
    res=[]
    whatis_str = m.modulewhatis(modname).split('\n')
    for item in whatis_str:
        if 'Categorie' in item:
            res.append(item.split()[-1])
    return res

def get_info(modname):
    
    res = {}
    help_str = m.modulehelp(modname)
    help_str=help_str.replace('\t', '')
    help_str=help_str.split('\n')
    fields=help_str[1].split()
    name, version = fields[5][1:-1].split('/')
    res["name"] = name 
    res["version"] = version
    #get commands list
    try:
        idx = help_str.index('package provides following commands:')
    except ValueError as err:
        idx = -1
    
    #get tool list
    tool_list = []
    if idx> 0: 
        tool_list = help_str[idx+1:]

    #start analyzing:
    help_str=help_str[6:idx]
    url_idx = warn_idx = i = 0
    for item in help_str:
        if "URL:" in item:
            _, homepage = item.split()
            res['homepage'] = homepage
            url_idx=i
        if 'WARNING' in item:
            warn_idx = i
            deps = item[item.find('<')+1:item.find('>')]
            fields = deps.split(' ')
            deps = list(set(fields))
            # remove extraneous and or tokens
            try:
                deps.remove('or')
                deps.remove('and')
                deps.remove('')
            except ValueError as err:
                pass
            res["uses"] = [d for d in deps if d]
        if "bioweb2" in item:
            res["docs"] = item
        i+=1
        
    if url_idx:
        res['description'] =' '.join(help_str[:url_idx])
    elif not url_idx and warn_idx:
        res['description'] = ' '.join(help_str[:warn_idx])
    else:
        res['description'] = ' '.join(help_str)
        
    # get internal categories from module display 
    edamcat = get_edam(modname)
    if edamcat:
        res['categories'] = edamcat
    else:
        print >> sys.stderr, "%s: no EDAM categories\n" %(modname)

    # grab author and publications from BIODOCS
    author, publications = get_refs(name)
    if author is not None:
        res['authors']  = ' '.join(author).split(',')
    if publications is not None:
        res['publications'] = publications

    #special_case for libraries:
    return res, tool_list
    
DOIFLAGS = ['doi', 'pmid', 'pmcid']

def extract_doi(item):
    tmp = item.lower()
    found = False
    for flag in DOIFLAGS:
        if flag in tmp:
            found = flag
    if not found:
        return item, None
    idx = tmp.find(found)
    citation = item[:idx]
    doi = tmp[idx:]
    citation = citation.strip()
    doi = doi.strip()
    return citation, doi

def get_refs(modname):
    bidocsfile =  os.path.join(INST, modname, 'BIODOCS')
    with open(bidocsfile, 'r') as fh:
        res = {}
        flag = None
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#'): continue

            if line.startswith('PACK') or line.startswith('PROG'):
                fields = line.split()
                k = fields[0].replace(':', '')
                flag = k
                v = " ".join(fields[1:])
                res[k] = res.get(k, []) + [ v ]
            else:
                if flag == 'PACK.REF':
                    if flag in res:
                        res[flag].append(line)
                    else:
                        res[flag] = [ line ]
                else:
                    v = line.split()
                    res[flag] = res.get(flag, []) + v

    authors = res.get('PACK.AUTHORS', None)
    if authors is not None:
        authors = [item.decode('latin-1') for item in authors if item]
    refs = res.get('PACK.REF', None)
    if refs is not None:
        refs = [item.decode('latin-1') for item in refs if item]
        # check if doi pmd or pmcid avalable: 
        for i, elem in enumerate(refs):
            citation, doi = extract_doi(elem) 
            if doi is not None:
                refs[i] = citation, doi 
            else:
                print >> sys.stderr, "%s : no doi" % (modname)

    return (authors, refs) 

def json_generator(pack, tools):
    #dump package
    pack_name = pack['name'] 
    pack_version = pack['version']
    pack_file = os.path.join(DEST, '%s_%s.json' % (pack_name, pack_version))
    print "write: %s" % (pack_file)
    with open(pack_file, 'w') as outfh:
        json.dump(pack, outfh, indent=INDENT)

    #now dump each tool
    #change type to tool instead of package     
    pack['software'] = 'Tool'
    # remove dependencies, as they may be non relevant ones.
    if 'uses' in pack:
        del pack['uses']
    # remove categories, authors and references as they are already documented in package xml.
    if 'authors' in pack:
        del pack['authors']
    if 'publications' in pack:
        del pack['publications']
    if 'categories' in pack:
        del pack['categories']

    for tool in tools:
        if not tool:
            continue
        tool_file = os.path.join(DEST, "%s_%s_%s.json" %(pack_name, pack_version, tool))
        print "write: %s" % (tool_file)
        pack['name'] = tool
        with open(tool_file, 'w') as outfh:
            json.dump(pack, outfh, indent=INDENT)


if __name__ == '__main__':

    
    if len(sys.argv) > 1:
        modules = sys.argv[1:]
    else:
        os.environ['MODULEPATH'] = MODPATH
        modules = m.moduleavail()
    

    for module in modules:
        print "<<<<<<<<<", module
        if not '/' in module:
            continue
        if module.startswith('test/') or module.startswith('alacon'):
            continue
        if 'default' in module: 
            module = module.replace('(default)', '')
        pack, tools = get_info(module)
        if not 'homepage' in pack:
            print >> sys.stderr, "%s/%s: missing HOME" %(pack['name'], pack['version'])
            continue
        if tools:
            pack['software'] = 'Suite'
        else:
            pack['software'] = 'Library'
        pack['collectionName'] = 'gensoft'
        pack['interfaces'] = 'command-line'
        try:
            json_generator(pack, tools)
        except:
            print >> sys.stderr, "%s/%s: problem" %(pack['name'], pack['version'])
