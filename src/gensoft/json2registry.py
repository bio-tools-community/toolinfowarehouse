#!/usr/bin/env python

"""
Created on Feb.3nd , 2015

@author:  Eric Deveaud
@contact: edeveaud@pasteur.fr
@project: toolinfowarehouse
@githuborganization: edamontology
@adapated from O.Doppelt tool: import_json_to_bioregistry.py 
"""

import argparse
import requests
import getpass
import json
import os
import sys

REGISTRY_API='https://elixir-registry.cbs.dtu.dk/api'
REGISTRY_AUTH='%s/auth/login' %(REGISTRY_API)
REGISTRY_TOOL='%s/tool' %(REGISTRY_API)

def get_credentials(login, identityfile):
    if identityfile is not None:
        try:
            with open(identityfile) as fh:
                for line in fh:
                    line=line.strip()
                    if line.startswith('#'):
                        continue
                    if line.startswith('login'):
                        _, login = line.split(':')
                    if line.startswith('passwd'):
                        _, password = line.split(':')
        except IOError as err:
            print >> sys.stderr, err
            sys.exit(1)
    else:
        if login is None:
            login= raw_input("Login: ")
        password = getpass.getpass()
    login=login.strip()
    password=password.strip()
    return  login, password



def auth(login, password):
    service = REGISTRY_AUTH
    req = '{"username": "%s","password": "%s"}' % (login, password)
    headers= {'Accept': 'application/json', 'Content-type': 'application/json'}
    resp = requests.post( service, req , headers=headers).text
    try:
        return json.loads(resp)['token']
    except KeyError as err:
        print >> sys.stderr, "Autentification failure", resp
        sys.exit(1)
    except:
        print >> sys.stderr, "something wen wrong ", resp
        sys.exit(1)
        
def drop_registry_info(login, token):
        print "attempting to delete all registered services..."
        service = '%s/%s' %(REGISTRY_TOOL, login)
        headers = { 'Accept':'application/json'
                  , 'Content-type':'application/json'
                  , 'Authorization': 'Token %s' % token
                  }
        resp = requests.delete(service, headers=headers)
        print resp
    
def insert_info(json_file, token):
    try:
        json_data = json.load(json_file)
    except Exception as err:
        print >> sys.stderr, "%s: error loading json: %s" %(json_file.name,err)
    headers = { 'Accept':'application/json'
              , 'Content-type':'application/json'
              , 'Authorization': 'Token %s' % token
              }
    resp = requests.post(REGISTRY_TOOL, json.dumps(json_data), headers=headers)
    if resp.status_code == 201:
        return  1
    else:
        json_name=os.path.basename(json_file.name)
        print >> sys.stderr, "%s, error: %s" %(json_name, resp.text)
        return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="import JSON to ELIXIR bioregistry")
    parser.add_argument("-l", "--login"
                       , help="Registry login"
                       , default=None
                       )

    parser.add_argument("-j", "--json_dir"
                       , help="Directory for the json to import"
                       )
    parser.add_argument("-i", "--identity"
                       , help="Identity file"
                       , default=None
                       )
    parser.add_argument("-d", "--delete"
                       , help="Drop registry infos"
                       , action="store_true"
                       , default=False)
    args = parser.parse_args()

    print "authenticating..."
    login, passwd = get_credentials(args.login, args.identity)
    token = auth(login, passwd)
    print "authentication ok"

    if args.delete:
        drop_registry_info(login, token)

    print "loading json"
    total = 0
    ok = 0
    for file in os.listdir(args.json_dir):
        if not file.endswith('.json'):
            continue
        with open(os.path.join(args.json_dir, file), 'r') as json_file:
            print >> sys.stdout, "%s" %(json_file.name), 
            total +=1
            ret= insert_info(json_file, token)
            ok += ret
            if ret:
                print >> sys.stdout, "ok" 
            else:
                print >> sys.stdout, 'ko'

    print >> sys.stdout, "total: %d [ok %d, ko %d]" %(total, ok, total-ok )





