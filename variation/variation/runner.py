import numpy as np
import numexpr as ne
import argparse
import re
import xml.etree.ElementTree as ET
import copy
import os
import glob
import shutil
from variation import dependencySolver as ds
from ctypes import *


args = None #global args object

def is_var(arg): #method just checks if the string validates against the RE
    m = re.search('\$\{.*\}', arg)
    if m==None:
        return False
    else:    
        return True

def get_var_val(key, ii, varDict):
    """Gets an input in the likes of ${var} and returns the corresponding var value from the dict

    Parameters
    ----------
    key: string
        unparsed key of var
    ii: int
        current iteration idx
    varDict: dict
        variable dictionary

    Returns
    -------
    string
        variable value as string

    """
    res = varDict.get(key[2:-1], '0')[ii]
    return str(res)

def find_var(item, idx, vars):
    """Recursively fills in the values of variables in the given data tree 

    Parameters
    ----------
    item: xml.etree.ElementTree.Element
        Tree item to traverse recursively
    idx: int
        current iteration idx
    vars: dict
        variable dictionary

    """
    for child in item.getchildren():
        find_var(child, idx, vars)
        for key, val in child.attrib.items():
            if is_var(val):
                child.attrib[key] = get_var_val(val, idx, vars)

def hasValue(key, varDict):
    return key in varDict

def generateVar(var, n):    
    """Generates a value for a given var node

    Parameters
    ----------
    var: xml.etree.ElementTree.Element
        Tree node containing info about the variable
    n: int
        number of output files

    Returns
    -------
    array[n]
        n dimensional array containing the values (or linear equation) for the variable

    """
    
    dist = var.get('type')
    if dist == 'normal':
        val = np.random.normal(float(var.get('mu')), float(var.get('sd')), n)
    elif dist == 'uniform':            
        val = np.random.uniform(float(var.get('min')), float(var.get('max')), n)
    elif dist == 'lindep':
        val = np.full(n, str(var.get("dp")))       
    else:       
        raise ValueError("A wrong or invalid distribution type was provided")

    return val


def executePipeline(n, tree, inpDir, nwName, varDict):
    """This method calls the roadGen Lib function for every rev

    Parameters
    ----------
    n: int 
        number of revs
    tree: ElementTree
        the tree struct generated from input
    inpDir: str
        input dir
    nwName: str
        new name generate from input name
    varDict: dict
        dict containing array of vars
    
    """

    for i in range(n):
        cpTree = copy.deepcopy(tree)
        if not cpTree.getroot().find('vars') == None:
            cpTree.getroot().remove(cpTree.getroot().find('vars'))        
        
        find_var(cpTree.getroot(), i, varDict)        
        tmpName = inpDir+ nwName + '_rev' + str(i) + '.xml'
        print("Running on " + tmpName)               
        cpTree.write(tmpName)
        
        if os.name == "posix":  # if MacOS
            libpath = os.path.join(os.path.dirname(__file__), "resources/libroad-generation.so")  
            xml_path = os.path.join(os.path.dirname(__file__), "resources/xml/") 

            roadgen = cdll.LoadLibrary(libpath) #load shared lib
            
            argFilename = c_char_p(tmpName.encode('utf-8')) #execute "main" function from lib 
            argXMLPath = c_char_p(xml_path.encode('utf-8'))  
            roadgen.setSilentMode(c_bool(args.s))
            roadgen.setFileName(argFilename)
            roadgen.setXMLSchemaLocation(argXMLPath)
            if args.o:
                outArgs = c_char_p((args.o+"_rev"+str(i)).encode('utf-8'))
                roadgen.setOutputName(outArgs)
            roadgen.execPipeline()

        else:   
            libpath = os.path.join(os.path.dirname(__file__), "resources/road-generation.dll")  
            roadgen = cdll.LoadLibrary(libpath) 
            
            argFilename = c_char_p(tmpName.encode('utf-8'))          
            roadgen.setSilentMode(c_bool(args.s))
            roadgen.setFileName(argFilename)
            if args.o:
                outArgs = c_char_p((args.o+"_rev"+str(i)).encode('utf-8'))
                roadgen.setOutputName(outArgs)
            roadgen.execPipeline()

def initDirectories(inpDir):
    if not os.path.exists(inpDir ):
        os.makedirs(inpDir )


def copyTemplate(path):
    shutil.copy(os.path.join(os.path.dirname(__file__), "resources/network.tmpl"), path)

def run():
    #parsing args-------------------------------------
    global args
    print("-- Let's start the road network variation")
    argParse = argparse.ArgumentParser()
    argParse.add_argument('-fname', help='filename of the road network template', metavar='<TemplateFilename>')
    argParse.add_argument('-o', help='set output name scheme', metavar='<out filename>')
    argParse.add_argument('-n', help='number of variations to be generated', metavar='<int>', type=int, default=20)
    argParse.add_argument('-e', help='generate an example template file', metavar='<file location>')
    argParse.add_argument('-k', help='keep intermediate xml files after generation', action='store_false')
    argParse.add_argument('-s', help='run roadgen in silent mode', action='store_true')
    args = argParse.parse_args()    

    
    if not args.e == None:
            copyTemplate(args.e)
            print("copied tmpl file to " + args.e)

    if args.fname == None:
        if args.e == None:
            print("Error:\n-fname <FileName> required.\nUse -h for further help.")
        return

    n = args.n
    clearOutputFolder = args.k   
    fname = args.fname
    nwName = str.split(str.split(fname,'/')[-1],'.')[0]
    inpDir = os.path.join(os.path.dirname(fname), "variation_output/")
    initDirectories(inpDir)  

    #init --------------------------------------------
    tree = ET.parse(args.fname)
    vars = tree.getroot().find('vars')
    varDict = {}
    #reading values-----------------------------------
    if not vars == None:
        for var in vars:
            val = generateVar(var, n)
            varDict.update({var.get('id'): val})

    #solving equations------------------------------------

        varList = ds.getVarLists(varDict, n)
        varDict = ds.solveEQ(varList, n)
    else:
        print("No variables detected. Running only one iteration!")
        n = 1
    #clear input folder
    files = glob.glob(inpDir+'*')
    for f in files:
        os.remove(f)

    executePipeline(n, tree, inpDir, nwName, varDict)

    #clear input folder (again)
    if clearOutputFolder :
        files = glob.glob(inpDir+'*.xml')
        for f in files:
            os.remove(f)

if __name__ == '__main__':
    run()