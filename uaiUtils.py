import io
from pathlib import Path

def initiateInputStream(f):
    fin = None;
    needToCloseFile = False;
    if isinstance(f, io.TextIOBase):
        fin = f;
    else:
        p = Path(f)
        fin = p.open('r')
    return fin, needToCloseFile

def initiateOutputStream(f):
    fout = None;
    needToCloseFile = False;
    if isinstance(f, io.TextIOBase):
        fout = f;
    else:
        p = Path(f)
        fout = p.open('w')
    return fout, needToCloseFile

def fullTableSizeFromDomains(f, uaiModel):
    ntuples = 1;
    for v in uaiModel["scopes"][f]:
        ntuples *= uaiModel["domainSizes"][v]
    return ntuples;

def readTokens(f):
    fin, needToCloseFile = initiateInputStream(f)
    tokens = []
    for line in fin:
        sline = line.strip()
        if not sline or not sline[0].isalnum():
            continue;
        tokens += sline.split()
    if needToCloseFile:
        fin.close()
    return tokens

def readUaiModel(f):
    uaiModel = {
                    "type"          :   None,
                    "nvars"         :   None,
                    "domainSizes"   :   None,
                    "nfxns"         :   None,
                    "scopes"        :   None,
                    "fxntbls"       :   None,
               }

    
    tokens = readTokens(f)

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

def printUaiModel(f, model):

    fout, needToCloseFile = initiateOutputStream(f)

    # print(,file=fout)
    print(model["type"],file=fout)
    print(file=fout)

    print(model["nvars"],file=fout)
    print(*model["domainSizes"],file=fout)
    print(file=fout)

    print(model["nfxns"],file=fout)
    for f in range(model["nfxns"]):
        print(len(model["scopes"][f]), *model["scopes"][f], file=fout)
    print(file=fout)

    for f in range(model["nfxns"]):
        print(len(model["fxntbls"][f]), file=fout)
        print(*model["fxntbls"][f], file=fout)
        print(file=fout)

    if needToCloseFile:
        fout.close()


def readEvid(evid_f, uai=None):
    evid = {}
    validityCheckedWrtUaiFile = False

    evidTokens = readTokens(evid_f)
    idx = 0
    evid["nevid"] = int(evidTokens[idx])
    idx += 1
    assert(evid["nevid"] >= 0), str(evid_f)
    assert(evid["nevid"]*2 == len(evidTokens)-1), str(evid_f)
    evid["assignments"] = {}
    for i in range(evid["nevid"]):
        var = int(evidTokens[idx])
        idx += 1
        ass = int(evidTokens[idx])
        idx += 1
        assert(var not in  evid["assignments"]), str(evid_f)
        evid["assignments"][var] = ass
    assert(idx == len(evidTokens)), str(evid_f)
    
    if uai != None:
        uaiModel = None
        if isinstance(uai, dict):
            uaiModel = uai;
        else:
            uaiModel = readUaiModel(uai)
        for v in evid["assignments"]:
            assert(v in range(uaiModel["nvars"])), str(evid_f)
            assert(evid["assignments"][v] in range(uaiModel["domainSizes"][v])), str(evid_f)
        validityCheckedWrtUaiFile = True

    return evid, validityCheckedWrtUaiFile


def readQuery(query_f, uai=None):
    query = {}
    validityCheckedWrtUaiFile = False

    queryTokens = readTokens(query_f)
    idx = 0
    query["nquery"] = int(queryTokens[idx])
    idx += 1
    assert(query["nquery"] >= 0), str(query_f)
    assert(query["nquery"] == len(queryTokens)-1), str(query_f)
    query["vars"] = set()
    for i in range(query["nquery"]):
        var = int(queryTokens[idx])
        idx += 1
        assert(var not in  query["vars"]), str(query_f)
        query["vars"].add(var)
    assert(idx == len(queryTokens)), str(query_f)
    
    if uai != None:
        uaiModel = None
        if isinstance(uai, dict):
            uaiModel = uai;
        else:
            uaiModel = readUaiModel(uai)
        for v in query["vars"]:
            assert(v in range(uaiModel["nvars"])), str(query_f)
        validityCheckedWrtUaiFile = True

    return query, validityCheckedWrtUaiFile

        

    
    
    
