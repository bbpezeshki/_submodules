import io
from pathlib import Path

def uaiFileTypes():
    res = set(['.uai','.evid','.query','.sum','.elim', '.ord','.map'])
    return res

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
    evid = {
        "nevid"         :   None,
        "assignments"   :   None, # dict
    }
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
    query = {
        "nquery"    :   None,
        "vars"    :   None,
    }
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

def toDictMPEStyleAssignments(tokens):
    asst = {
        "nassignments"  :   None,
        "assignments"   :   None, # dict
    }
    idx = 0
    asst["nassignments"] = int(tokens[idx])
    idx += 1
    asst["assignments"] = {}
    var = -1;
    numInvalidAss = 0;
    for i in range(ass["nassignments"]):
        var += 1
        ass = int(tokens[idx])
        idx += 1
        if ass == -1:
            numInvalidAss +=1
            continue;
        assert(var not in  ass["assignments"]), str(f)
        asst["assignments"][var] = ass
    assert(idx == len(tokens)), str(f)
    assert(var+1 == asst["nassignments"])
    asst["nassignments"] -= numInvalidAss
    return ass;

def toDictMMAPStyleAssignments(tokens):
    asst = {
        "nassignments"  :   None,
        "assignments"   :   None, # dict
    }
    idx = 0
    asst["nassignments"] = int(tokens[idx])
    idx += 1
    asst["assignments"] = {}
    numInvalidAss = 0
    for i in range(asst["nassignments"]):
        var = int(tokens[idx])
        idx += 1
        ass = int(tokens[idx])
        idx += 1
        if ass == -1:
            numInvalidAss +=1
            continue;
        assert(var not in  asst["assignments"]), str(f)
        asst["assignments"][var] = ass
    assert(idx == len(tokens)), str(f)
    asst["nassignments"] -= numInvalidAss
    return asst

def readAssignments(f):
    # assumes on a single line
    
    asses = {
        "nsets"     :   0,
        "sets"      :   [], 
    }
    
    fin, needToCloseFile = initiateInputStream(f)
    for line in fin:
        tokens = []
        sline = line.strip()
        if not sline or not sline[0].isalnum():
            continue;
        tokens += sline.split()
        try:
            n = int(tokens[0])
        except:
            continue;
        ass = {}
        if len(tokens[1:])==n:
            # MPE full assignment
            asses["sets"].append(toDictMPEStyleAssignments(tokens))
            asses["nsets"] += 1
        elif len(tokens[1:])==n*2:
            # MMAP or ass assignment
            asses["sets"].append(toDictMMAPStyleAssignments(tokens))
            asses["nsets"] += 1
        else:
            #invalid solution line
            continue; 
    if needToCloseFile:
        fin.close()

    return asses

def extractLastAssignmentsDict(data):
    lastAssDict = None
    if isinstance(data, dict):
        if "assignments" in data:
            lastAssDict = {int(k):int(v) for k,v in data["assignments"].items()}
        elif "sets" in data:
            lastAssDict = {int(k):int(v) for k,v in data["sets"][-1]["assignments"].items()}
        else:
            lastAssDict = {int(k):int(v) for k,v in data.items()}
    else: # extract from file
        asses = readAssignments(data)
        lastAssDict = asses["sets"][-1]["assignments"]
    return lastAssDict

def compareLastAssignments(in1,in2):
    a1 = extractLastAssignmentsDict(in1)
    a2 = extractLastAssignmentsDict(in2)

    matchingAssignments = {}
    mismatchingAssignments = {}
    assignmentsMissingIn1 = set()
    assignmentsMissingIn2 = set()
    for var in a1:
        if var in a2:
            if a1[var] == a2[var]:
                matchingAssignments[var] = a1[var]
            else:
                mismatchingAssignments[var] = (a1[var],a2[var],)
        else:
            assignmentsMissingIn2.add(var)
    for var in a2:
        if var not in a1:
            assignmentsMissingIn1.add(var)
    return matchingAssignments, mismatchingAssignments, assignmentsMissingIn1, assignmentsMissingIn2


def truncateMAPtoMMAP(map_output_file, mmap_query_file, new_truncated_map_file):
    map_output_file = Path(map_output_file).absolute();
    mmap_query_file = Path(mmap_query_file).absolute();
    new_truncated_map_file = Path(new_truncated_map_file).absolute();

    n_map_vars = None
    map_vars = None
    map_assignments = None
    tokens = None
    with map_output_file.open('r') as fin:
        tokens = []
        for line in fin:
            line = line.strip()
            if line == "" or line=="-BEGIN-":
                continue;
            tokens += line.split()
    n_map_vars = int(tokens[0])
    map_vars = [int(x) for x in tokens[1::2]]
    map_assignments = [int(x) for x in tokens[2::2]]
    assert(len(map_vars) == len(map_assignments) == n_map_vars)
    map_assignment_tuples = dict(zip(map_vars,map_assignments))


    n_mmap_query_vars = None
    mmap_query_vars = None
    tokens = None
    with mmap_query_file.open('r') as fin:
        tokens = []
        for line in fin:
            line = line.strip()
            if line == "":
                continue;
            tokens += line.split()
    n_mmap_query_vars = int(tokens[0])
    mmap_query_vars = [int(x) for x in tokens[1:]]
    assert(len(mmap_query_vars) == n_mmap_query_vars)
    assert(n_mmap_query_vars <= n_map_vars)


    with new_truncated_map_file.open('w') as fout:
        print(n_mmap_query_vars, end=" ", file=fout)
        for i in mmap_query_vars:
            print(i, map_assignment_tuples[i], sep=" ", end=" ", file=fout)
        print(file=fout)

    

    
    
    

