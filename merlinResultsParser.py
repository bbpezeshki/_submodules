import math

from pathlib import Path
from collections import OrderedDict

from readlines import readLinesUntil

SPLITTER_IDX = 0
ENTRY_TITLE_IDX = 1
TEXT_TO_REMOVE_IDX = 2
DELETE_ENTRY_LOOKUP_IDX = 3

preprocessingLines = OrderedDict([
                            (   "Min fxn value:"            ,    (':',       None,                            [],             True)       ),
                            (   "Min non-zero fxn value:"   ,    (':',       None,                            [],             True)       ),
                            (   "Max fxn value:"            ,    (':',       None,                            [],             True)       ),
                            (   "Number of tuples:"         ,    (':',       None,                            [],             True)       ),
                            (   "Number of zero tuples:"    ,    (':',       None,                            [],             True)       ),
                            (   "Determinism ratio:"        ,    (':',       None,                            [],             True)       ),
                            (   "Created problem with"      ,    ('with',    "Problem before evidence",     [".",],         True)       ),
                            (   "Removed evidence, now"     ,    ('now',     "Problem after evidence",      [".",],         True)       ),
                            (   "Global constant:"          ,    (':',       None,                            [],             True)       ),
                            (   "Max. domain size:"         ,    (':',       None,                            [],             True)       ),
                            (   "Max. function arity:"      ,    (':',       None,                            [],             True)       ),
                            (   "Graph with"                ,    ('with',    "Graph",                       ["created.",],   True)       ),
                            (   "Read QUERY variables"      ,    ('(',       "Num Query Vars",              [").",],         True)       ),
                            (   "QUERY:"                    ,    (':',       "Query Vars",                  [],             True)       ),
                            (   "MAP:"                      ,    (':',       "MAP Vars",                    [],             True)       ),
                            (   "Generated constrained"     ,    (':',       "Elim Ord",                    [],             True)       ),
                            (   "Number of disconnected"    ,    (':',       "Disconnected pseudo trees",   [],             True)       ),
                            (   "Induced width:"            ,    (':',       "w*",                          [],             True)       ),
                            (   "Pseudotree depth:"         ,    (':',       "d",                           [],             True)       ),
                            (   "Start pseudotree:"         ,    (':',       None,                            [],             True)       ),
                            (   "Problem variables:"        ,    (':',       None,                            [],             True)       ),
                            (   "Disconn. components:"      ,    (':',       None,                            [],             True)       ),
                            (   "Determinism below:"        ,    (',',       "CP construction",             ["so", ".",],   True)       ),
                            (   "Problem loaded in"         ,    (' in ',      "Problem load time",           ["onds.",],          True)       ),
                            (   "Created SAT"               ,    ('with',    "CP construction",             [],             False)       ),
                            (   "Initial SAT instance"      ,    (' is ',      "Initial CP",                  [],             False)       ),
                            (   "Determinism encoded and"   ,    (' in ',      "Initial CP time",             ["onds.",],          False)       ),
                            (   "final tmin:"               ,    (':',       "t-max SAT",                            [],             True)       ),
                            (   "Ufo deflation factor:"     ,    (':',       None,                            [],             True)       ),
                            (   "Underflow threshold that"  ,    (':',       "t-final",                            [],             True)       ),
                            (   "Time to deflate"           ,    (':',       "Heuristic deflation time",    [],             True)       ),
                            (   "New iB"                    ,    (':',       "iB",                          [],             True)       ),
                            (   "Computing"                 ,    ('Computing',"Hueristic init",             [".",],          True)       ),
                            (   "Use scope only?"           ,    ('?',       None,                            [],             True)       ),
                            (   "Weighted Mini-Buckets?"    ,    ('?',       None,                            [],             True)       ),
                            (   "Moment Matching?"          ,    ('?',       None,                            [],             True)       ),
                            (   "MAP log Bound"             ,    ('Bound',   None,                            [],             True)       ),
                            (   "Build Bound:"              ,    (':',       None,                            [],             True)       ),
                            (   "Log Bound:"                ,    (':',       None,                            [],             True)       ),
                            (   "Mini bucket finished in"   ,    (' in ',      "MBE time",                    [],             True)       ),
                            (   "Using"                     ,    ('Using',   "MBE memory",                  ["of RAM",],     True)       ),
                            (   "Heuristic is exact!"       ,    (' is ',      "Exact initial heuristic?",    [],             True)       ),
                            (   "Initialization complete:"  ,    (':',       "Preprocessing time",          [],             True)       ),
                        ])

preprocessingEndLines = [
                            "Starting search",
                            "Solved during initialization",
                        ]

kstarInitLines = [
                    "BBK* Wild-type log10 K* Value:",
                    "BBK* Wild-type ln K* Value:",
                    "BBK* Wild-type log10 Subunit Z Values:",
                    "Wild-type ln Subunit Z Values:",
                    "subunitStabilityThresholdAdjustment:",
                    "m_subunitStabilityThresholds:",
                 ]



def get_search_line_tokens(line):
    newSearchBound = False;
    search_line_tokens = None;
    line_split_by_time = line[1:].split("]");
    time = line_split_by_time[0];
    if "*" not in time:
        newSearchBound = True;
    time = time.replace("*","").strip();
    line_excluding_time = line_split_by_time[1].replace('(',"").replace(')',"");
    search_line_tokens = [time] + line_excluding_time.split();
    return search_line_tokens, newSearchBound;

def parse_any_ldfs_bounded_search_line(line):
    search_line_data = OrderedDict()
    search_line_tokens, newSearchBound = get_search_line_tokens(line);
    search_line_data["time"] = search_line_tokens[0]
    search_line_data["log lower bound"] = search_line_tokens[6];
    search_line_data["log upper bound"] = search_line_tokens[8];
    return search_line_data, newSearchBound;

def parse_any_rbfaoo_ublb_search_line(line):
    search_line_data = OrderedDict()
    search_line_tokens, newSearchBound = get_search_line_tokens(line);
    search_line_data["time"] = search_line_tokens[0]
    search_line_data["log lower bound"] = search_line_tokens[7];
    search_line_data["log upper bound"] = search_line_tokens[9];
    return search_line_data, newSearchBound;

def parse_any_sbfs_bounded_search_line(line):
    search_line_data = OrderedDict()
    search_line_tokens, newSearchBound = get_search_line_tokens(line);
    search_line_data["time"] = search_line_tokens[0]
    search_line_data["log lower bound"] = search_line_tokens[6];
    search_line_data["log upper bound"] = search_line_tokens[8];
    return search_line_data, newSearchBound;

def parse_aobb_search_line(line):
    search_line_data = OrderedDict()
    search_line_tokens, newSearchBound = get_search_line_tokens(line);
    search_line_data["time"] = search_line_tokens[0]
    search_line_data["log lower bound"] = search_line_tokens[8];
    search_line_data["log upper bound"] = "";
    return search_line_data, newSearchBound;

def parse_rbfaoo_search_line(line):
    search_line_data = OrderedDict()
    search_line_tokens, newSearchBound = get_search_line_tokens(line);
    search_line_data["time"] = search_line_tokens[0]
    search_line_data["log lower bound"] = search_line_tokens[5];
    search_line_data["log upper bound"] = "";
    return search_line_data, newSearchBound;


ALGORITHM_TO_SEARCH_LINE_PARSER_Dict = { "any-ldfs-bounded"		:		parse_any_ldfs_bounded_search_line,
                                         "any-rbfaoo-ublb"		:		parse_any_rbfaoo_ublb_search_line,
                                         "any-sbfs-bounded"		:		parse_any_sbfs_bounded_search_line,
                                         "aobb"					:		parse_aobb_search_line,
                                         "ufo-aobb"				:		parse_aobb_search_line,
                                         "braobb"				:		parse_aobb_search_line,
                                         "rbfaoo"				:		parse_rbfaoo_search_line,
                                         "kstar-aobb"			:		parse_aobb_search_line,
                                         "ufo-kstar-aobb"	    :		parse_aobb_search_line,
                                         }

NUM_NEW_SEARCH_BOUNDS_TO_RECORD = 5
SEARCH_TIME_POINTS_TO_RECORD = [0.1, 1.0, 5.0, 10.0, 20.0, 60.0, 120.0, 300.0, 1200.0]
SEARCH_TIME_POINTS_TO_RECORD.sort();


#####################################################################################################################
#####################################################################################################################

def updateSearchBound(last_searchBoundData, search_line_data):
    last_searchBoundData["f last bound improvement time"] = float(search_line_data["time"])
    last_searchBoundData["last bound improvement time"] = search_line_data["time"]
    last_searchBoundData["last bound improvement ln lb"] = search_line_data["log lower bound"]
    last_searchBoundData["last bound improvement log10 lb"] = str(float(search_line_data["log lower bound"])/math.log(10))
    last_searchBoundData["last bound improvement ln ub"] = search_line_data["log upper bound"]
    last_searchBoundData["last bound improvement log10 ub"] = "" if search_line_data["log upper bound"]=="" else str(float(search_line_data["log upper bound"])/math.log(10))

def recordSearchPoint(data_summary, last_searchBoundData, searchPointDescription):
    data_summary[searchPointDescription + ": time"] = last_searchBoundData["last bound improvement time"]
    data_summary[searchPointDescription + ": ln lower bound"] = last_searchBoundData["last bound improvement ln lb"]
    data_summary[searchPointDescription + ": log10 lower bound"] = last_searchBoundData["last bound improvement log10 lb"]
    data_summary[searchPointDescription + ": ln upper bound"] = last_searchBoundData["last bound improvement ln ub"]
    data_summary[searchPointDescription + ": log10 upper bound"] = last_searchBoundData["last bound improvement log10 ub"]

def updateSearchPointWithLastRecorded(data_summary, lastSearchPointDescriptionRecorded, searchPointDescription):
    data_summary[searchPointDescription + ": time"] = data_summary[lastSearchPointDescriptionRecorded + ": time"]
    data_summary[searchPointDescription + ": ln lower bound"] = data_summary[lastSearchPointDescriptionRecorded + ": ln lower bound"]
    data_summary[searchPointDescription + ": log10 lower bound"] = data_summary[lastSearchPointDescriptionRecorded + ": log10 lower bound"]
    data_summary[searchPointDescription + ": ln upper bound"] = data_summary[lastSearchPointDescriptionRecorded + ": ln upper bound"]
    data_summary[searchPointDescription + ": log10 upper bound"] = data_summary[lastSearchPointDescriptionRecorded + ": log10 upper bound"]

def processSearchLine(algorithm, extractedLine, last_searchBoundData, newSearchBoundCounter, data_summary, timepointsLeftToRecord, last_searchTimePointKeyStem_recorded):
    search_line_data, newSearchBound = ALGORITHM_TO_SEARCH_LINE_PARSER_Dict[algorithm](extractedLine)
    finalSearchLineData = search_line_data
    if newSearchBound == True and float(search_line_data["log lower bound"]) > float("-inf"):
        updateSearchBound(last_searchBoundData, search_line_data)
        newSearchBoundCounter += 1;
        if newSearchBoundCounter <= NUM_NEW_SEARCH_BOUNDS_TO_RECORD:
            newSearchBoundKeyStem = "new search bound " + str(newSearchBoundCounter)
            recordSearchPoint(data_summary, last_searchBoundData, searchPointDescription=newSearchBoundKeyStem)
    timepoint = float(search_line_data["time"])
    newSearchTimePointsFinalizedIdx = [];
    for i, timePointToRecord in enumerate(timepointsLeftToRecord):
        newSearchTimePointKeyStem = "search timepoint (" + str(timePointToRecord) + " sec)"
        if timepoint <= (timePointToRecord+min(timePointToRecord*0.05, 0.1)):
            if last_searchBoundData["last bound improvement time"] != None:
                recordSearchPoint(data_summary, last_searchBoundData, searchPointDescription=newSearchTimePointKeyStem)
                last_searchTimePointKeyStem_recorded = newSearchTimePointKeyStem
            break;
        else:
            if last_searchBoundData["f last bound improvement time"] <= (timePointToRecord+min(timePointToRecord*0.05, 0.1)):
                recordSearchPoint(data_summary, last_searchBoundData, searchPointDescription=newSearchTimePointKeyStem)
                last_searchTimePointKeyStem_recorded = newSearchTimePointKeyStem
            else:
                if last_searchTimePointKeyStem_recorded != None:
                    updateSearchPointWithLastRecorded(data_summary, last_searchTimePointKeyStem_recorded, searchPointDescription=newSearchTimePointKeyStem)
            newSearchTimePointsFinalizedIdx.append(i)
    reversed_newSearchTimePointsRecordedIdx = reversed(newSearchTimePointsFinalizedIdx)
    for idxToDel in reversed_newSearchTimePointsRecordedIdx:
        del timepointsLeftToRecord[idxToDel]

    return finalSearchLineData, newSearchBoundCounter, last_searchTimePointKeyStem_recorded



def summarizeData(experiment_files_by_type_Dict, root=None):
    data_summary = OrderedDict()
    stdout_file_Path = experiment_files_by_type_Dict["stdout"];
    stderr_file_Path = None
    if "stderr" in experiment_files_by_type_Dict:
        stderr_file_Path = experiment_files_by_type_Dict["stderr"];	

    # extract information from stdout
    if root != None:
        data_summary["stdout file path"] = str(stdout_file_Path.relative_to(root));
    else:
        data_summary["stdout file path"] = str(stdout_file_Path.absolute())
    with stdout_file_Path.open('r') as stdout_file:
        for i in range(1):
            
            # SKIP PROGRAM TITLE AND INFO
            prevLine, extractedLine, matchFound, matchType, matchIdx, numLinesReadIn = \
                readLinesUntil(stdout_file, _startswith="--------------------------------", _strip=True, _prevLine=None)
            if matchFound==True:
                assert(numLinesReadIn==1)
            else:
                break;

            prevLine, extractedLine, matchFound, matchType, matchIdx, numLinesReadIn = \
                readLinesUntil(stdout_file, _startswith="--------------------------------", _strip=True, _prevLine=extractedLine)
            if matchFound==False:
                break;
        

            # EXTRACT COMMAND LINE INPUT
            prevLine, extractedLine, matchFound, matchType, matchIdx, numLinesReadIn = \
                readLinesUntil(stdout_file, _startswith="", _strip=True, _prevLine=extractedLine, _maxNumLines=1)
            if matchFound==True:
                assert(numLinesReadIn==1)
            else:
                break;
            data_summary["Command line input"] = extractedLine.strip();


            # EXTRACT PROGRAM ARGUMENT PRINTOUTS
            prevLine, extractedLine, matchFound, matchType, matchIdx, numLinesReadIn = \
                readLinesUntil(stdout_file, _startswith="+ i-bound:", _strip=True, _prevLine=extractedLine)
            if matchFound==False:
                break;
            line_tokens = extractedLine.split(":");
            iB = line_tokens[1].strip();
            data_summary["iB"] = iB;

            while(matchFound==True):
                prevLine, extractedLine, matchFound, matchType, matchIdx, numLinesReadIn = \
                    readLinesUntil(stdout_file, _startswith="+", _strip=True, _prevLine=extractedLine, _maxNumLines=1)
                if matchFound==True:
                    line_tokens = extractedLine.split(":");
                    key = line_tokens[0].split('+')[1].strip()
                    value = line_tokens[1].strip();
                    data_summary[key] = value;
                    if key == "Algorithm":
                        algorithm = value # store algorithm in variable in case we need to do algorithm specific output extractions


            # EXTRACT PREPROCESSING INFORMATION
            lineIdentifiers = list(preprocessingLines.keys());
            matchIdx = None;
            matchedString = None;
            # while(matchedString!="--- Starting search ---" and matchedString!="--------- Solved during initialization ---------"):
            while(True):
                prevLine, extractedLine, matchFound, matchType, matchIdx, numLinesReadIn = \
                    readLinesUntil(stdout_file, _startswith=lineIdentifiers, _contains=preprocessingEndLines, _strip=True, _prevLine=extractedLine)
                if matchFound == False:
                    break; # reached EOF
                if matchType == "_contains":
                    matchedString = preprocessingEndLines[matchIdx]
                    break; # reaached one of the preprocessingEndLines
                matchedString = lineIdentifiers[matchIdx]
                splitter = preprocessingLines[matchedString][SPLITTER_IDX]
                textToRemove = preprocessingLines[matchedString][TEXT_TO_REMOVE_IDX]
                deleteLineIdentifier = preprocessingLines[matchedString][DELETE_ENTRY_LOOKUP_IDX]
                key = preprocessingLines[matchedString][ENTRY_TITLE_IDX]
                if key==None:
                    key = matchedString.replace(':',"").strip()
                value = extractedLine.split(splitter)[1]
                for toRemove in textToRemove:
                    value = value.replace(toRemove,"")
                value = value.strip()
                data_summary[key] = value
                if deleteLineIdentifier == True:
                    del lineIdentifiers[matchIdx]
            if "Hueristic init" in data_summary and "i=" in data_summary["Hueristic init"]:
                finaliB = data_summary["Hueristic init"].split('=')[1].split(')')[0]
                data_summary["iB"] = finaliB
            if "Determinism ratio" in data_summary:
                data_summary["Determinism ratio"] = str( round( (float(data_summary["Determinism ratio"].replace('%',""))/100.0), 2 ) )
            if matchFound == False:
                break; # reached EOF            
            

            # PROCESS SEARCH OUTPUT
            if matchedString == "Starting search":
                finalSearchLineData = None;
                timepointsLeftToRecord = SEARCH_TIME_POINTS_TO_RECORD.copy()
                newSearchBoundCounter = 0;
                last_searchTimePointKeyStem_recorded = None
                last_searchBoundData = {
                    "f last bound improvement time" : float('nan'),
                    "last bound improvement time" : None,
                    "last bound improvement ln lb" : None,
                    "last bound improvement log10 lb" : None,
                    "last bound improvement ln ub" : None,
                    "last bound improvement log10 ub" : None,
                }

                lineIdentifiers = kstarInitLines.copy()
                prevLine, extractedLine, matchFound, matchType, matchIdx, numLinesReadIn = \
                    readLinesUntil(stdout_file, _startswith=lineIdentifiers, _contains=["[", "Search done"], _strip=True, _prevLine=extractedLine)
                matchedString = None
                while matchFound:
                    if matchType == "_startswith":
                        matchedString = lineIdentifiers[matchIdx]
                        del lineIdentifiers[matchIdx]
                        splitLine = extractedLine.split(":")
                        key = splitLine[0].strip()
                        val = splitLine[1].strip()
                        data_summary[key] = val
                        prevLine, extractedLine, matchFound, matchType, matchIdx, numLinesReadIn = \
                            readLinesUntil(stdout_file, _startswith=lineIdentifiers, _contains=["[", "Search done"], _strip=True, _prevLine=extractedLine)
                    else: # matchType == "_contains"
                        if matchIdx==0: # matched with "["
                            matchedString = "["
                            finalSearchLineData, newSearchBoundCounter, last_searchTimePointKeyStem_recorded = \
                                processSearchLine(algorithm, extractedLine, last_searchBoundData, newSearchBoundCounter, data_summary, timepointsLeftToRecord, last_searchTimePointKeyStem_recorded)
                        else: # matched with "Search done"
                            matchedString = "Search done"
                            pass;
                        break;

                if matchFound and matchedString == "[":
                    while matchFound:
                        prevLine, extractedLine, matchFound, matchType, matchIdx, numLinesReadIn = \
                            readLinesUntil(stdout_file, _startswith="[", _contains="Search done", _strip=True, _prevLine=extractedLine)
                        if matchFound == False:
                            break; # reached EOF
                        if matchType == "_contains":
                            break; # reaached end of search
                        finalSearchLineData, newSearchBoundCounter, last_searchTimePointKeyStem_recorded = \
                            processSearchLine(algorithm, extractedLine, last_searchBoundData, newSearchBoundCounter, data_summary, timepointsLeftToRecord, last_searchTimePointKeyStem_recorded)
                
                if last_searchTimePointKeyStem_recorded != None:
                    for tp in timepointsLeftToRecord:
                        searchTimePointKeyStem = "search timepoint (" + str(tp) + " sec)"
                        updateSearchPointWithLastRecorded(data_summary, last_searchTimePointKeyStem_recorded, searchPointDescription=searchTimePointKeyStem)                   
                
                finalSearchTimePointKeyStem = "final search timepoint"
                if finalSearchLineData != None:
                    recordSearchPoint(data_summary, last_searchBoundData, searchPointDescription=finalSearchTimePointKeyStem)

                # store last found bound data
                for kk in last_searchBoundData:
                    if type(last_searchBoundData[kk])==float:
                        continue;
                    if last_searchBoundData[kk] != None:
                        data_summary[kk] = last_searchBoundData[kk]

                if "last bound improvement time" in data_summary:
                    f_anytime = float(data_summary["last bound improvement time"].replace("seconds","").strip()) + float(data_summary["Preprocessing time"].replace("seconds","").strip())
                    data_summary["Anytime"] = str(f_anytime)

                if matchFound == False:
                    break; # reached EOF

            
            # FINAL SUMMARY
            while(matchFound==True):
                prevLine, extractedLine, matchFound, matchType, matchIdx, numLinesReadIn = \
                    readLinesUntil(stdout_file, _contains=":", _strip=True, _prevLine=extractedLine, _maxNumLines=1)
                if matchFound==True:
                    line_tokens = extractedLine.split(":");
                    key = line_tokens[0].strip()
                    value = line_tokens[1].strip();
                    if key == "Solution":
                        full_solution_printout_tokens = value.split();
                        solution = full_solution_printout_tokens[0].strip();
                        data_summary["Solution"] = solution;
                        ln_solution = full_solution_printout_tokens[1].replace('(','').replace(')','').strip();
                        data_summary["Solution (ln)"] = ln_solution;
                        data_summary["Solution (log10)"] = str(float(ln_solution)/math.log(10));
                    else:
                        data_summary[key] = value;

            # APPENDED INFORMATION
            while(numLinesReadIn > 0):
                prevLine, extractedLine, matchFound, matchType, matchIdx, numLinesReadIn = \
                    readLinesUntil(stdout_file, _contains=":", _strip=True, _prevLine=extractedLine, _maxNumLines=1)
                if matchFound==True:
                    line_tokens = extractedLine.split(":");
                    key = line_tokens[0].strip()
                    value = line_tokens[1].strip();
                    data_summary[key] = value;
    

    # extract information from stderr
    if stderr_file_Path:
        data_summary["stderr file path"] = str(stderr_file_Path.relative_to(root));
        with stderr_file_Path.open('r') as stderr_file:
            for i, line in enumerate(stderr_file):
                data_summary["error line " + str(i)] = line.strip();

    return data_summary;