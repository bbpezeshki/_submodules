import io
from pathlib import Path
from collections import defaultdict
from copy import deepcopy

def uaiFileTypes():
    res = set(['.uai','.evid','.query','.sum','.elim', '.ord','.map'])
    return res

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

def fullTableSizeFromDomains(f, uaiModel):
    ntuples = 1;
    for v in uaiModel["scopes"][f]:
        ntuples *= uaiModel["domainSizes"][v]
    return ntuples;

def readTokens(f, accepted_non_lnum=set()):
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

def readUaiModel(uai_f):
    uaiModel = {
                    "type"          :   None,
                    "nvars"         :   None,
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


def removeConstantFxn(model, onlyIfOne=True):
    constantFxnIdx = None;
    for i, scope in enumerate(model["scopes"]):
        if len(scope) == 0:
            assert(constantFxnIdx == None)
            constantFxnIdx = i;

    constantFxnFound = (constantFxnIdx != None)
    
    if constantFxnFound:
        assert(len(model["fxntbls"][constantFxnIdx]) == 1)
        if onlyIfOne == True:
            assert(model["fxntbls"][constantFxnIdx][0] == 1)
        model["nfxns"] -= 1;
        del model["scopes"][i];
        del model["fxntbls"][i];
    
    return constantFxnFound


def writeUaiModel(f, model):

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


def readElim(elim_f, uai=None):
    elim = {
                    "nvars"         :   None,
                    "vars"          :   None,
                    "order"         :   None,
               }

    elimTokens = readTokens(elim_f)
    idx = 0
    elim["nvars"] = int(elimTokens[idx])
    idx += 1
    assert(elim["nvars"] >= 0), str(elim_f)
    assert(elim["nvars"] == len(elimTokens)-1), str(elim_f)
    elim["vars"] = set()
    elim["order"] = []
    for i in range(elim["nvars"]):
        var = int(elimTokens[idx])
        idx += 1
        assert(var not in  elim["vars"]), str(elim_f)
        elim["vars"].add(var)
        elim["order"].append(var)
    assert(idx == len(elimTokens)), str(elim_f)
    assert(len(elim["order"])==len(set(elim["order"])))
    
    if uai != None:
        uaiModel = None
        if isinstance(uai, dict):
            uaiModel = uai;
        else:
            uaiModel = readUaiModel(uai)
        uaiVars = set(range(uaiModel["nvars"]))
        for v in elim["vars"]:
            assert(v in uaiVars), str(elim_f)

    return elim


def reverseOrder(order_input, uai=None, inPlace=False):
    order = None
    filename = None
    if type(order_input) == dict:
        order = order_input
        if not inPlace:
            order = deepcopy(order)
        assert(all(x in order_input for x in ["nvars", "vars", "order"]))
        assert(len(order["order"])==len(set(order["order"])))
        if uai != None:
            uaiModel = None
            if isinstance(uai, dict):
                uaiModel = uai;
            else:
                uaiModel = readUaiModel(uai)
            uaiVars = set(range(uaiModel["nvars"]))
            for v in order_input["vars"]:
                assert(v in uaiVars), str(order_input)
    else:
        assert(type(order_input) == str or type(order_input) == Path)
        order = readElim(order_input, uai=uai)
    oldFirst = order["order"][0]
    order["order"].reverse()
    assert(oldFirst == order["order"][-1])
    
    return order



def writeOrder(f, order):
    fout, needToCloseFile = initiateOutputStream(f)
    print(order["nvars"], file=fout)
    print(*order["order"], file=fout)
    if needToCloseFile:
        fout.close()

    

def readEvid(evid_f, uai=None):
    evid = {
        "nevid"         :   None,
        "assignments"   :   None, # dict
    }

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
        uaiVars = set(range(uaiModel["nvars"]))
        for v in evid["assignments"]:
            assert(v in uaiVars), str(evid_f)
            assert(evid["assignments"][v] in range(uaiModel["domainSizes"][v])), str(evid_f)

    return evid


def readQuery(query_f, uai=None):
    query = {
        "nquery"    :   None,
        "vars"    :   None,
    }

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
        uaiVars = set(range(uaiModel["nvars"]))
        for v in query["vars"]:
            assert(v in uaiVars), str(query_f)

    return query

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



def rewriteElimForAS(elim_f):
    oldFile = Path(elim_f)
    order = readElim(oldFile)
    oldFile.unlink()
    outfile = Path(elim_f).with_suffix(".elim")
    with outfile.open('w') as fout:
        print('#', file=fout)
        print(order["nvars"], file=fout)
        print(*order['order'], sep='\n',file=fout)

    

# def extractNextBifComponent(tokens):
#     component = {
#         "type" : None,
#         "name" : None,
#         "data" : None,
#     }
#     idx = 0
#     subTokens = token[0].split()
#     assert(len(subTokens)==3 and subTokens[2] == "{")
#     component["type"] = subTokens[0]
#     component["name"] = subTokens[1]
#     data = []
#     idx +=1
#     while tokens[idx] != "}":
#         data.append(tokens[idx])
#         idx += 1

#     return tokens[idx+1:], component


# def extractBifComponents(f):
#     bif_components = defaultdict(list)
#     tokens = readTokens(f, accepted_non_lnum={"}"})
#     while len(tokens) != 0:
#         tokens, component = extractNextBifComponent(tokens)
#         bif_component[component["type"]].append(component)

#     return bif_components


# def extractBifVariables(bif_components):
#     for component in bif_components["variable"]
#         variable = {
#             "name" : None,
#             "type" : None,
#             "ds_to_di" : None,
#         }
#         assert(component["type"]=="variable")
#         assert(len(component["data"])==1)
#         assert(component["data"][0][-1]==";") #type discrete [ 3 ] { LOW, NORMAL, HIGH };
#         variable["name"] = component["name"]
#         tokens = component["data"][0].split()
#         assert(tokens[0]=="type")
#         variable["type"] = tokens[1]
#         assert(tokens[2]=="[" and tokens[4]=="]")
#         dsize = int(tokens[3])
#         assert(tokens[5]=="{" and tokens[6+dsize]=="};")
#         dtokens = tokens[5+1:6+dsize]
#         ds_to_di = {}
#         for di,ds enumerate(dtokens):
#             ds_to_di[ds.replace(",","")] = di


# def convertBifToUai(f):
#     uaiModel = {
#                     "type"          :   None,
#                     "nvars"         :   None,
#                     "domainSizes"   :   None,
#                     "nfxns"         :   None,
#                     "scopes"        :   None,
#                     "fxntbls"       :   None,
#                }

#     bif_components = extractBifComponents(f)

    
    

    
    

