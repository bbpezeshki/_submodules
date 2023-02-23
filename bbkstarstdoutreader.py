from pathlib import Path
from readlines import readLinesUntil
from collections import defaultdict




def parseDesign(line):
    tokens = line.split()
    assert(tokens[0] == "DESIGN:"), tokens[0]
    design = tokens[1]
    return design


def parsePDB(line):
    tokens = line.split()
    assert(tokens[0] == "PDB:")
    pdbtokens = tokens[1].split(".")
    pdb = ".".join(pdbtokens[-1])
    return pdb


def parseBBKstarSolutionLine(line):
    solution = {}
    
    tokens = line.split()
    assert(tokens[0] == "sequence")

    # extract sequence number
    sequenceNumber = tokens[1].replace("/"," ").split()[0]
    int(sequenceNumber)
    
    # extract sequence
    idx_KstarLog10 = tokens.index("K*(log10):")
    sequence = {}
    for i in range(3,idx_KstarLog10):
        aa_assignment = tokens[i].split("=")
        sequence[aa_assignment[0]] = aa_assignment[1]
    
    # extract K*
    idx_protein = tokens.index("protein:")
    assert(tokens[idx_protein-1] == "(log10)");
    kstar = {}
    estimate = None
    lb = None
    ub = None
    for i in range(idx_KstarLog10, idx_protein):
        if i == (idx_KstarLog10 + 1):
            try:
                float(tokens[i])
                estimate = tokens[i]
            except:
                pass; # sometime's bbkstar's estimate is "none" for some reason, though it still produces bounds for its solution; here we just save None for the estimate and comtinue to extracting the bounds
        elif i == (idx_KstarLog10 + 3):
            t = tokens[i].replace(","," ").split()
            lb = t[0].replace("[","")
            float(lb)
            if len(t)==2:
                assert(i == idx_protein-2);
                ub = t[1].replace("]","")
                float(ub)
                break; # we've extracted all the needed info
        elif i == (idx_protein-2):
            t = tokens[i].replace(","," ").split()
            assert(len(t)==1)
            ub = t[0].replace("]","")
            float(ub)
            break; # we've extracted all the needed info
    kstar["estimate"] = str(estimate) # sometimes bbkstar's estimate is "none" for some reason
    kstar["lb"] = lb
    kstar["ub"] = ub

    # extract protein
    idx_ligand = tokens.index("ligand:")
    assert(tokens[idx_ligand-2] == "epsilon:" or tokens[idx_ligand-2] == "delta:"), tokens[idx_ligand-2]
    protein = {}
    lb = None
    ub = None
    for i in range(idx_protein, idx_ligand):
        if i == (idx_protein + 1):
            t = tokens[i].replace(","," ").split()
            lb = t[0].replace("[","")
            float(lb)
            if len(t)==2:
                ub = t[1].replace("]","")
                float(ub)
                break; # we've extracted all the needed info
        elif i == (idx_protein + 2):
            t = tokens[i].replace(","," ").split()
            if len(t)==1:
                ub = t[0].replace("]","")
                float(ub)
                break; # we've extracted all the needed info
        elif i == (idx_protein + 3):
            t = tokens[i].replace(","," ").split()
            assert(len(t)==1)
            ub = t[0].replace("]","")
            float(ub)
            break; # we've extracted all the needed info
    protein["lb"] = lb
    protein["ub"] = ub

    # extract ligand
    idx_complex = tokens.index("complex:")
    assert(tokens[idx_complex-2] == "epsilon:" or tokens[idx_complex-2] == "delta:"), tokens[idx_complex-2]
    ligand = {}
    lb = None
    ub = None
    for i in range(idx_ligand, idx_complex):
        if i == (idx_ligand + 1):
            t = tokens[i].replace(","," ").split()
            lb = t[0].replace("[","")
            float(lb)
            if len(t)==2:
                ub = t[1].replace("]","")
                float(ub)
                break; # we've extracted all the needed info
        elif i == (idx_ligand + 2):
            t = tokens[i].replace(","," ").split()
            if len(t)==1:
                ub = t[0].replace("]","")
                float(ub)
                break; # we've extracted all the needed info
        elif i == (idx_ligand + 3):
            t = tokens[i].replace(","," ").split()
            assert(len(t)==1)
            ub = t[0].replace("]","")
            float(ub)
            break; # we've extracted all the needed info
    ligand["lb"] = lb
    ligand["ub"] = ub

    # extract complex
    assert(tokens[-2] == "epsilon:" or tokens[-2] == "delta:"), tokens[-2]
    complexed = {}
    lb = None
    ub = None
    for i in range(idx_complex, len(tokens)):
        if i == (idx_complex + 1):
            t = tokens[i].replace(","," ").split()
            lb = t[0].replace("[","")
            float(lb)
            if len(t)==2:
                ub = t[1].replace("]","")
                float(ub)
                break; # we've extracted all the needed info
        elif i == (idx_complex + 2):
            t = tokens[i].replace(","," ").split()
            if len(t)==1:
                ub = t[0].replace("]","")
                float(ub)
                break; # we've extracted all the needed info
        elif i == (idx_complex + 3):
            t = tokens[i].replace(","," ").split()
            assert(len(t)==1)
            ub = t[0].replace("]","")
            float(ub)
            break; # we've extracted all the needed info
    complexed["lb"] = lb
    complexed["ub"] = ub


    solution["sequence number"] = sequenceNumber
    solution["sequence"] = sequence
    solution["kstar"] = kstar
    solution["protein"] = protein
    solution["ligand"] = ligand
    solution["complex"] = complexed
    
    return solution


def parseTime(line):
    tokens = line.split()
    assert(tokens[0] == "ELAPSED")
    assert(tokens[1] == "TIME:")
    time = tokens[2]
    return time


parsingFunctions = {
                    "design"    :   parseDesign,
                    "pdb"       :   parsePDB,
                    "wildtype"  :   parseBBKstarSolutionLine,
                    "kstarMAP"  :   parseBBKstarSolutionLine,
                    "time"      :   parseTime,
                    "success"   :   lambda x: True,     #simply returns true when called with any argument
                    }


def extractNextEntry(fin, onlyReturnCompleteEntries=True):
    entry = {}
    matchKeys = ["DESIGN:", "PDB:", "sequence", "sequence", "ELAPSED TIME:", "============================================="]
    entryKeys = ["design", "pdb", "wildtype", "kstarMAP", "time", "success"]
    for i, matchkey in enumerate(matchKeys):
        # print("matchKey:", matchkey)
        prevLine, currLine, matchFound, matchType, matchIdx, numLinesReadIn = \
            readLinesUntil(_fin=fin, _startswith=[matchkey], _strip=True)
        if not matchFound:
            if onlyReturnCompleteEntries or len(entry)==0:
                entry = None
            break;
        entry[entryKeys[i]] = parsingFunctions[entryKeys[i]](currLine)
    return entry
    


def extractBBKstarStdoutInfoFromFile(bbkstar_file_path):
    bbkstarFile = Path(bbkstar_file_path)
    assert(bbkstarFile.is_file())
    stdoutInfo = defaultdict(dict)
    prevLine = None
    currLine = None
    with bbkstarFile.open('r') as fin:
        continueExtractingANextEntry = True
        while(continueExtractingANextEntry):
            entry = extractNextEntry(fin)
            if entry == None:
                continueExtractingANextEntry = False
            else:
                baseDesignNumber = int(entry["design"].split("_")[0])
                stdoutInfo[baseDesignNumber][entry["design"]] = entry
    return stdoutInfo

        