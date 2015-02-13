#! /usr/bin/env python

"""
Created on Feb.2nd , 2015

@author: Eric Deveaud, Institut Pasteur, Paris
@contact: edeveaud@pasteur.fr
@project: toolinfowarehouse
@githuborganization: edamontology
"""





import sys
from pprint import pprint 

#---- globals

#---- PACKAGES KEYS 
pack_mandatory_keys = [ 'NAME'
                      , 'CATEGORIES'
                      , 'DESCRIPTION'
                      , 'VERSION'
                      ]

pack_other_keys = { 'HOME' : ''
                  , 'SOURCE' : ''
                  , 'AUTHORS' : []
                  , 'HTMLDOCS' : []
                  , 'MANPAGES' : []
                  , 'REF' : []
                  }
     
pack_gensoft_keys = { 'HISTORY' : []
                    , 'LIBRARY' : ''
                    , 'PRIVATE' : ''
                    , 'RESTRICT' : ''
                    }
pack_accessory_keys = { 'MAINTAINER' : ''
                      , 'LICENSE' : ''
                      , 'LANGUAGE' : []
                      }
     

#---- PROGRAMS KEYS 
prog_mandatory_keys = [ 'NAME'
                     ]

prog_other_keys = { 'DESCRIPTION' : ''
                  , 'CATEGORIES' : []
                  , 'MANPAGES' : []
                  , 'HTMLDOCS' : []
                  }

prog_gensoft_keys = { 'PRIVATE' : ''
                    , 'RESTRICT' : ''
                    }

prog_mobyle_keys = { 'WEB' : ''
                   }

pack_accessory_keys = { 'USE' : []
                      }


def get_doi(item):
    '''
    extract doi from reference entry
    returns reference, doi
    '''
    DOIFLAGS = ['doi', 'pmid', 'pmcid']
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

def get_value(data):
    '''
    for internal use
    split biodocs TAGS: value
    return TAG name, associated value
    '''
    # double colon may appears in value
    fields = data.split(':')
    tag = fields[0]
    value = ':'.join(fields[1:]).strip()
    _, tag  = tag.split('.')
    return  tag, value

def get_pack(fh):
    '''
    package specific definition entries parser
    returns a dictionary 
    '''
    res = {}

    #---- deal with package definitions.
    while True:
        pos = fh.tell()
        line = fh.readline()
        if not line:
            break
        line = line.strip()

        if not line or line.startswith('#'):
            continue

        line = line.decode('iso-8859-1').encode('utf-8') 
        if line.startswith('PROG'):
            fh.seek(pos,0)
            break
        #--- skip values
        elif line.startswith('PACK.USE'):
            pass
        elif line.startswith('PACK.MAINTAINER'):
            pass
       
        #---- One line one value entries
        elif line.startswith('PACK.NAME'): 
            k, v = get_value(line)
            res[k] = v
        elif line.startswith('PACK.HOME'):
            k, v = get_value(line)
            res[k] = v
        elif line.startswith('PACK.SOURCE'):
            k, v = get_value(line)
            res[k] = v
        elif line.startswith('PACK.AUTHORS'):
            k, v = get_value(line)
            v = v.split(',')
            res[k] = v
        elif line.startswith('PACK.LICENSE'):
            k, v = get_value(line)
            res[k] = v
        elif line.startswith('PACK.LIBRARY'):
            k, v = get_value(line)
            res[k] = v
        elif line.startswith('PACK.PRIVATE'):
            k, v = get_value(line)
            res[k] = v
        elif line.startswith('PACK.RESTRICT'):
            k, v = get_value(line)
            res[k] = v

        #---- One line multi values entries
        elif line.startswith('PACK.VERSION'):
            k, v = get_value(line)
            res[k] = v.split()
        elif line.startswith('PACK.CATEGORIES'):
            k, v = get_value(line)
            res[k] = v.split()
        elif line.startswith('PACK.HTMLDOCS'):
            k, v = get_value(line)
            res[k] = [v]
        elif line.startswith('PACK.LANGUAGE'):
            k, v = get_value(line)
            res[k] = v.split()
        
        #---- multi line entries
        elif line.startswith('PACK.DESCRIPTION'):
            k, v = get_value(line)
            res[k] = [v]
        elif line.startswith('PACK.REF'):
            k, v = get_value(line)
            res[k] = [v]
        elif line.startswith('PACK.HISTORY'):
            k, v = get_value(line)
            res[k] = [v]

        #---- problems to fix, report
        elif line.startswith('PACK'):   
            print >> sys.stderr, "unknown PACK tag:",  line
            sys.exit(1)

        else:
            res[k].append(line)
    return res


def get_progs(fh):
    '''
    program entries parser
    return a dictionary of programs description as dictionary
    key = progname : value = prog information as dictionary
    '''
        
    prog_lst = []

    #---- deal with prog definitions.
    prog = {}
    line = fh.readline() 
    while line:
        line = line.strip()

        if not line:
            if prog: # avoid empty progs based on multiple empty lines
                prog_lst.append(prog)
            prog = {}
        elif line.startswith('PROG.USE'):
            pass
        elif line.startswith('PROG.PRIVATE'):
            pass
        elif  line.startswith('#'):
            pass

        elif line.startswith('PROG.NAME'):
            k, v = get_value(line)
            prog[k] = v
        elif line.startswith('PROG.DESCRIPTION'):
            k, v = get_value(line)
            prog[k] = [v]
        elif line.startswith('PROG.CATEGORIES'):
            k, v = get_value(line)
            prog[k] = v.split()
        elif line.startswith('PROG.HTMLDOCS'):
            k, v = get_value(line)
            prog[k] = [v]
        elif line.startswith('PROG.MANPAGES'):
            k, v = get_value(line)
            prog[k] = [v]

        #---- One line multi values entries
        elif line.startswith('PROG.WEB'):
            k, v = get_value(line)
            prog[k] = [v]

        #---- problems to fix, report
        elif line.startswith('PROG'):
            print >> sys.stderr, "unknown PROG tag:",  line
            sys.exit(1)
        elif line.startswith('PACK'):
            print >> sys.stderr, "unknown PACK tag PROGS section:",  line
            sys.exit(1)

        else:
            prog[k].append(line)
        line = fh.readline() 

    if prog:
        prog_lst.append(prog)
    return prog_lst


def pack_consolidate(datas):
    '''
    fill missing entries on pack
    inplace modification
    '''
    #--- check for package mandatory keys
    for key in pack_mandatory_keys:
        if key not in datas:
            print >> sys.stderr, datas['NAME'], 'missing PACK mandatory key', key
            sys.exit(1)
    #--- silently insert missing packages keys
    checks =  [pack_other_keys, pack_gensoft_keys]
    for item in checks:
        for key, default_val in item.items():
            if key not in datas:
                datas[key] = default_val
                

def progs_consolidate(datas):
    '''
    fills prog descriptions entries with missing info
    inplace modification
    '''
    for prog in datas:
        if not prog:
            continue
        #--- check for programs mandatory keys
        for key in prog_mandatory_keys:
            if key not in prog:
                print >> sys.stderr, 'missing PROG mandatory key', key
                sys.exit(1)
        #--- silently insert missing programs keys
        checks =  [prog_other_keys, prog_gensoft_keys]
        for item in checks:
            for key, default_value in item.items():
                if key not in prog:
                    prog[key] = default_value


def Parser(fh):
    '''
    parsing of BIODOCS files, returned as a dictionary
        Key == BIODOC tag
        Val == content
    WARNING:  NO semantic verification
    '''    
    pack = get_pack(fh)
    progs = get_progs(fh)
    if not progs and not 'LIBRARY' in pack:
        print sys.stderr, "no programs description found"
    pack_consolidate(pack)
    progs_consolidate(progs)

    return pack, progs



if __name__ == '__main__':
    for biodocs in sys.argv[1:]:
        print biodocs
        fh = open(biodocs)
        pack, progs = Parser(fh)
        fh.close()


