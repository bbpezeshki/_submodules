import io
from pathlib import Path
from collections import defaultdict
from copy import deepcopy


# fin, needToCloseFile = initiateInputStream(f)
def initiateInputStream(f):
    fin = None;
    needToCloseFile = False;
    if isinstance(f, io.TextIOBase):
        fin = f;
    else:
        p = Path(f)
        fin = p.open('r')
        needToCloseFile = True
    return fin, needToCloseFile

# fout, needToCloseFile = initiateInputStream(f)
def initiateOutputStream(f):
    fout = None;
    needToCloseFile = False;
    if isinstance(f, io.TextIOBase):
        fout = f;
    else:
        p = Path(f)
        fout = p.open('w')
        needToCloseFile = True
    return fout, needToCloseFile

def readTokens(f, accepted_non_lnum=set('}')):
    fin, needToCloseFile = initiateInputStream(f)
    tokens = []
    for line in fin:
        sline = line.strip()
        if not sline:
            continue;
        if not sline[0].isalnum() and sline[0] not in accepted_non_lnum:
            continue;
        tokens += sline.split()
    if needToCloseFile:
        fin.close()
    return tokens

def extractVariableInfo(tokens,idx):
    variable = {
        "type"          :   None,
        "cardinality"   :   None,
        "domain"        :   None,
    }
    assert(tokens[idx]=="type"); idx+=1
    variable["type"] = tokens[idx]; idx +=1
    assert(variable["type"]=="discrete"), "no support for non-discrete currently"
    variable["cardinality"] = int(tokens[idx]); idx+=1
    variable["domain"] = [None] * cardinality
    for i in range(variable["cardinality"]):
        variable["domain"][i] = tokens[idx]; idx+=1
    assert(tokens[idx] == "}")
    return variable, idx



def extractNextEntry(tokens, idx=0):
    category = tokens[idx]; idx += 1;
    name = tokens[idx]; idx += 1;




def readUaiModel(uai_f):
    uaiModel = {
                    "type"          :   None,
                    "variables"     :   None,
                    "domainSizes"   :   None,
                    "nfxns"         :   None,
                    "scopes"        :   None,
                    "fxntbls"       :   None,
               }

    
    tokens = readTokens(uai_f)

    idx = 0
    uaiModel["type"] = tokens[idx]
    idx +=1;
    uaiModel["nvars"] = int(tokens[idx])
    idx +=1;

    domainSizes = [None]*uaiModel["nvars"]
    for i in range(uaiModel["nvars"]):
        domainSizes[i] = int(tokens[idx])
        idx += 1
    uaiModel["domainSizes"] = domainSizes

    uaiModel["nfxns"] = int(tokens[idx])
    idx += 1;
    scopes = [None] * uaiModel["nfxns"]
    for f in range(uaiModel["nfxns"]):
        scope = None;
        scopeSize = int(tokens[idx])
        idx += 1
        scope = [None]*scopeSize
        for s in range(scopeSize):
            scope[s] = int(tokens[idx])
            idx += 1
        scopes[f] = scope
    uaiModel["scopes"] = scopes

    fxntbls = [None] * uaiModel["nfxns"]
    for f in range(uaiModel["nfxns"]):
        ntuples = int(tokens[idx])
        assert(ntuples==fullTableSizeFromDomains(f,uaiModel)), str(f)
        idx += 1
        table = [None]*ntuples
        for t in range(ntuples):
            table[t] = float(tokens[idx])
            idx += 1
        fxntbls[f] = table
    uaiModel["fxntbls"] = fxntbls

    assert(idx==len(tokens)), str(f)

    return uaiModel