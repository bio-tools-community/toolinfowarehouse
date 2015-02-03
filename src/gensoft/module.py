"""
Created on Feb.2nd , 2015

@author: Eric Deveaud, Institut Pasteur, Paris
@contact: edeveaud@pasteur.fr
@project: toolinfowarehouse
@githuborganization: edamontology

A python wrapper to the Module Environment command.
see http://modules.sourceforge.net/

Warning: requires Module Environment  >= 3.3.* not yet released
pre 3.3 version may silently fail on some commands dur to exit values
of modulecmd non consistent. 

 initial author: Robert Minsk (egbert@centropolisfx.com)
 Feb   1, 2001          Robert Minsk (egbert@centropolisfx.com)
      * init file for python added
 Oct  1, 2010          R.K. Owen (rk@owen.sj.ca.us)
     * sed dependency removed
     * name changing  
 Sep 15,1014         Eric Deveaud (edeveaud@pasteur.fr)
     * some code rewrite
     * added python bindings to common calls to module command
"""

import collections
import os
import re
import subprocess
import sys

#--- check for module installation  
if 'MODULESHOME' not in os.environ:
    raise OSError("missing MODULESHOME definition or non available Module Environment")
   
#--- set necesssary env var if not already positioned
if  'MODULEPATH' not in os.environ:
    initfile = os.path.join(os.environ['MODULESHOME'], 'init', '.modulespath')
    with open(initfile, "r") as infh:
        modulepath = []
        for line in infh:
            #---- comment character `#' may be in any position
            line = line.split('#')[0].strip()
            if  line:
                modulepath.append(line)
    os.environ['MODULEPATH'] = ":".join(modulepath)

if 'LOADEDMODULES' not in os.environ:
    os.environ['LOADEDMODULES'] = ''

#---- get full path to modulecmd if defined in environment else fallback
#  to one availble in path
# If PY_MODULECMD is defined, Modulecmd will always  use its value
# to invoke modulecmd. Otherwise, it will attempt to invoke "modulecmd",
# relying on it being in the PATH.
_modulecmd_ = os.environ.get('PY_MODULECMD', "modulecmd")
#---- check for command availability
with open(os.devnull, 'w') as _DEVNULL:
    try:
        subprocess.check_call([_modulecmd_, "-V"], stdout=_DEVNULL, stderr=_DEVNULL)
    except OSError as err:
        raise OSError("missing MODULESHOME definition or non available Module Environment")



#---- for python 2 & 3 compatibility
def _b(x):
    if sys.version < '3':
        return x
    else:
        return x.decode()

def module(*args):
    """
    wrapper to the module command.
    accept the same switches, subcommand and subcommands-args  
    than the shell command
    for subcommand with display information returns a tuple composed by
    stdout and stderr (where results are) execution of modulecmd.
    otherwise None is returned and the environment is modified regarding 
    the executed module subcommand.
    """
    if isinstance(args[0], list):
        args = args[0]
    elif isinstance(args[0], str):
        args = args[0].split()
    else:
        args = list(args)
    # -=-=-=-=-=-=-=-=-=-=-  WARNING  -=-=-=-=-=-=-=-=-=-=-
    interpreter = 'python'
    try:
        module_process = subprocess.Popen(
            [_modulecmd_, interpreter] + args,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
						close_fds=True)
    except OSError as msg:
        raise OSError(msg)
    (output, error) = module_process.communicate()
    #deal with different type returned by subprocess beetwen python-2 and python-3
    output = _b(output)
    error = _b(error)
    if module_process.returncode != 0:
        msg = "module command failure"
        raise RuntimeError(msg, output, error)

    #---- check for submited module subcommand
    #---- for those that display info on stderr,  return results to caller
    verbose_command = (
        'display', 'show', 'avail', 'av', 'list', 
        'help', 'whatis', 'apropos', 'keyword',
        '-V', '--version', '-H', '--help',
        )
    for subcommand in verbose_command:
        if subcommand in args:
            return output, error
    #--- non verbose command do the job
    exec(output)



def _subcommand_runner(subcommand, *args):
    '''
    internal subcommand dipsatcher
    '''

    if not args:
        args = []
    elif isinstance(args[0], list):
        args = args[0]
    elif isinstance(args[0], tuple):
        args = list(args[0])
    else:
        args = list(args)

    ret = None
    #---- module managment subcommands
    if subcommand in ('add', 'load', 'rm', 'unload', 'switch', 'swap'):
        module([subcommand] + args)
    elif subcommand in ('purge', 'refresh'):
        module(subcommand)
    elif subcommand in ('list', 'av', 'avail', 'available'):
        # force -terse switch in order to facilitate results parsing  
        _, e = module([subcommand] + ['-t'] + args)
        if subcommand == 'list':
            ret = [item for item in e.split('\n') if item and 'Currently Loaded' not in item]
        else:
            ret = [item for item in e.split('\n') if item and not  item.startswith('/')]
    #---- modulepath managment subcommands
    elif subcommand in ('use', 'unuse'):
        module([subcommand]  + args)
    #---- module informative  subcommand 
    elif subcommand in ('display', 'show', 'help', 'whatis', 'apropos', 'keyword'):
        _, ret = module([subcommand] + args)
        #ret = ret.split('/n')
    else:
        raise ValueError("unknow subcommand {0}".format(subcommand))
    return ret
         

def moduleload(*args):
    '''
    Load modulefile(s) into the environment
    '''
    return _subcommand_runner('load', *args)


def moduleunload(*args):
    '''
    Remove modulefile(s) from the environment.
    '''
    return _subcommand_runner('unload', *args)


def moduleswap(modulefile1, *modulefile2):
    '''
    Switch loaded  modulefile1  with  modulefile2.
    If   modulefile2  is  not specified,  then  it is assumed to be the
    currently loaded module with the  same root name as
    modulefile1.
    '''
    return _subcommand_runner('swap', modulefile1, *modulefile2)


def moduledisplay(*args):
    '''
    Return as a string the  information    about   one   or   more
    modulefiles.  moduledisplay  will  list
    the  full  path  of the modulefile(s) and all (or
    most)   of   the    environment    changes    the
    modulefile(s)  will make if loaded.
    '''
    return _subcommand_runner('display', *args)

def moduleapropos(*args):
	'''
	Seeks through  the  'whatis'  informations  of  all  modulefiles
	for  the specified string.
	 All module-whatis informations matching the string will be displayed.
	'''
	return _subcommand_runner('apropos', *args)

def moduleavail(*args, **icase):
    '''
    returns a list of modulefiles matching the given prefix.
    icase: case insensitive search if True
                otherwise case sensitive search
    '''
    cmd = 'av'
    if icase:
        return _subcommand_runner('av', '-i', *args)
    return _subcommand_runner(cmd, *args)


def moduleuse(*args, **append_path):
    '''
    Prepend  one  or  more directories to the MODULEPATH environment
    variable.
    when append_path=True is given on the arguments, directories will be
    appended to MODULEPATH 
    '''
    #---- check  directories
    #for d in args:
    #    if not os.path.isdir(d):
    #        raise IOError(d, 'no such file or directory') 
    if append_path:
        return _subcommand_runner('use', '-a',  *args)
    return _subcommand_runner('use', *args)


def moduleunuse(*args):    
    '''
    Remove  one  or   more   directories   from   the
    MODULEPATH environment variable.
    '''
    return _subcommand_runner('unuse', *args)


def modulerefresh():
    '''
    Force  a refresh of all non-persistent components
    of currently loaded modules.
    '''
    return _subcommand_runner('refresh')


def modulepurge():
    '''
    Unload all loaded modulefiles.
    '''
    return _subcommand_runner('purge')


def modulelist():
    '''
    returns a list of currently loaded modulefiles.
    '''
    return _subcommand_runner('list')

def modulehelp(*args):
    '''
    Print  the  usage of each sub-command.  If an argument is given, print the
    Module-specific help information for the modulefile(s)
    '''
    return _subcommand_runner('help', *args)

def getmoduleversion():
    '''
    returns modules version as string
    '''
    import re
    output, error = module('--version')
    refilter = re.compile('VERSION=(?P<version>(.*))\n')
    hit =  refilter.search(error)
    if not hit:
        raise RuntimeError("unknow format: {0}".format(error))
    return  hit.group('version')


def modulewhatis(*args):
    '''
    retur as a string  the information set  up  by  the  module-
    whatis     commands    inside    the    specified
    modulefile(s). If no modulefile is specified, all
    'whatis' lines will be shown.
    '''
    return _subcommand_runner('whatis', *args)

#---- currently broken due to modulecmd exiting with failure return value 
#---- need work to be done on the C code of modulecmd

def _moduleapropos(*args):
    '''
    Seeks  through  the  'whatis' informations of all
    modulefiles  for  the  specified   string.
    '''
    return _subcommand_runner('whatis', *args)


"""
#---- pasteur internal, will maybee find is way to final distribution.

#---- structure describing the modules
modulefile = collections.namedtuple("modulefile", "name default versions")

def _av2tuple(lst):
    m = {}
    pattern = '.*/(?P<vdef>.*)\(default\)'
    automat = re.compile(pattern) 
    for item in lst:
        #---- get name and version numbers
        fields = item.split(os.sep)
        name = fields[0]
        version = []
        if len(fields) > 1:
            version = ["/".join([e.replace('(default)', '')  for e in   fields[1:]])]
        #---- versions[0] will contain the default version is found else None
        m[name] = m.get(name, [None]) + version 
        #---- get default version if present
        hit = automat.search(item)
        if hit:
            default = hit.group('vdef')
            m[name][0] = default
    #--- convert all to named tuple
    availablemodules = []
    for name in m:
        vdef = m[name][0]
        versions = m[name][1:]
        availablemodules.append(modulefile(name, vdef, versions)) 
    return availablemodules



def module2soft(*args):
    for m in args:
        helpmod = modulehelp(m).split('\n')
        i = 0
        for item in helpmod:
            i+=1
            if item == 'package provides following commands:':
                break
        return [item[1:] for item in helpmod[i:] if item]
        
"""
