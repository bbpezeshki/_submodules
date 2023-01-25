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
                                         }

NUM_NEW_SEARCH_BOUNDS_TO_RECORD = 5
SEARCH_TIME_POINTS_TO_RECORD = [0.1, 1.0, 5.0, 10.0, 20.0, 60.0, 120.0, 300.0, 1200.0]
SEARCH_TIME_POINTS_TO_RECORD.sort();


#####################################################################################################################
#####################################################################################################################

def summarizeData(experiment_files_by_type_Dict, root=Path("")):
    data_summary = OrderedDict()
    stdout_file_Path = experiment_files_by_type_Dict["stdout"];
    stderr_file_Path = None
    if "stderr" in experiment_files_by_type_Dict:
        stderr_file_Path = experiment_files_by_type_Dict["stderr"];	

    # extract information from stdout
    data_summary["stdout file path"] = str(stdout_file_Path.relative_to(root));
    with stdout_file_Path.open('r') as stdout_file:
        for i in range(1):
            
            # SKIP PROGRAM TITLE AND INFO
            prevLine, extractedLine, matchFound, match, numLinesReadIn = \
                readLinesUntil(stdout_file, _startswith="--------------------------------", _strip=True, _prevLine=None)
            if matchFound==True:
                assert(numLinesReadIn==1)
            else:
                break;

            prevLine, extractedLine, matchFound, match, numLinesReadIn = \
                readLinesUntil(stdout_file, _startswith="--------------------------------", _strip=True, _prevLine=extractedLine)
            if matchFound==False:
                break;
        

            # EXTRACT COMMAND LINE INPUT
            prevLine, extractedLine, matchFound, match, numLinesReadIn = \
                readLinesUntil(stdout_file, _startswith="", _strip=True, _prevLine=extractedLine, _maxNumLines=1)
            if matchFound==True:
                assert(numLinesReadIn==1)
            else:
                break;
            data_summary["Command line input"] = extractedLine.strip();


            # EXTRACT PROGRAM ARGUMENT PRINTOUTS
            prevLine, extractedLine, matchFound, match, numLinesReadIn = \
                readLinesUntil(stdout_file, _startswith="+ i-bound:", _strip=True, _prevLine=extractedLine)
            if matchFound==False:
                break;
            line_tokens = extractedLine.split(":");
            iB = line_tokens[1].strip();
            data_summary["iB"] = iB;

            while(matchFound==True):
                prevLine, extractedLine, matchFound, match, numLinesReadIn = \
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
                prevLine, extractedLine, matchFound, match, numLinesReadIn = \
                    readLinesUntil(stdout_file, _startswith=lineIdentifiers, _contains=preprocessingEndLines, _strip=True, _prevLine=extractedLine)
                if matchFound == False:
                    break; # reached EOF
                matchType = match[0]
                matchIdx = match[1]
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
            finalSearchLineData = None;
            timepointsLeftToRecord = SEARCH_TIME_POINTS_TO_RECORD.copy()
            newSearchBoundCounter = 0;
            if matchedString == "Starting search":
                last_searchTimePointKeyStem_recorded = None
                f_last_time = float('nan')
                last_time = None
                last_ln_lb = None
                last_log10_lb = None
                last_ln_ub = None
                last_log10_ub = None
                while(True):
                    prevLine, extractedLine, matchFound, match, numLinesReadIn = \
                        readLinesUntil(stdout_file, _startswith="[", _contains="Search done", _strip=True, _prevLine=extractedLine)
                    if matchFound == False:
                        break; # reached EOF
                    matchType = match[0]
                    if matchType == "_contains":
                        break; # reaached end of search
                    search_line_data, newSearchBound = ALGORITHM_TO_SEARCH_LINE_PARSER_Dict[algorithm](extractedLine)
                    finalSearchLineData = search_line_data
                    if newSearchBound == True and float(search_line_data["log lower bound"]) > float("-inf"):
                        f_last_time = float(search_line_data["time"])
                        last_time = search_line_data["time"]
                        last_ln_lb = search_line_data["log lower bound"]
                        last_log10_lb = str(float(search_line_data["log lower bound"])/math.log(10))
                        last_ln_ub = search_line_data["log upper bound"]
                        last_log10_ub = "" if search_line_data["log upper bound"]=="" else str(float(search_line_data["log upper bound"])/math.log(10))
                        newSearchBoundCounter += 1;
                        if newSearchBoundCounter <= NUM_NEW_SEARCH_BOUNDS_TO_RECORD:
                            newSearchBoundKeyStem = "new search bound " + str(newSearchBoundCounter) + ": "
                            data_summary[newSearchBoundKeyStem + "time"] = last_time
                            data_summary[newSearchBoundKeyStem + "ln lower bound"] = last_ln_lb
                            data_summary[newSearchBoundKeyStem + "log10 lower bound"] = last_log10_lb
                            data_summary[newSearchBoundKeyStem + "ln upper bound"] = last_ln_ub
                            data_summary[newSearchBoundKeyStem + "log10 upper bound"] = last_log10_ub
                    timepoint = float(search_line_data["time"])
                    newSearchTimePointsFinalizedIdx = [];
                    for i, timePointToRecord in enumerate(timepointsLeftToRecord):
                        newSearchTimePointKeyStem = "search timepoint (" + str(timePointToRecord) + " sec): "
                        if timepoint <= (timePointToRecord+min(timePointToRecord*0.05, 0.1)):
                            if last_time != None:
                                data_summary[newSearchTimePointKeyStem + "time"] = last_time
                                data_summary[newSearchTimePointKeyStem + "ln lower bound"] = last_ln_lb
                                data_summary[newSearchTimePointKeyStem + "log10 lower bound"] = last_log10_lb
                                data_summary[newSearchTimePointKeyStem + "ln upper bound"] = last_ln_ub
                                data_summary[newSearchTimePointKeyStem + "log10 upper bound"] = last_log10_ub
                                last_searchTimePointKeyStem_recorded = newSearchTimePointKeyStem
                            break;
                        else:
                            if f_last_time <= (timePointToRecord+min(timePointToRecord*0.05, 0.1)):
                                data_summary[newSearchTimePointKeyStem + "time"] = last_time
                                data_summary[newSearchTimePointKeyStem + "ln lower bound"] = last_ln_lb
                                data_summary[newSearchTimePointKeyStem + "log10 lower bound"] = last_log10_lb
                                data_summary[newSearchTimePointKeyStem + "ln upper bound"] = last_ln_ub
                                data_summary[newSearchTimePointKeyStem + "log10 upper bound"] = last_log10_ub
                                last_searchTimePointKeyStem_recorded = newSearchTimePointKeyStem
                            else:
                                data_summary[newSearchTimePointKeyStem + "time"] = data_summary[last_searchTimePointKeyStem_recorded + "time"]
                                data_summary[newSearchTimePointKeyStem + "ln lower bound"] = data_summary[last_searchTimePointKeyStem_recorded + "ln lower bound"]
                                data_summary[newSearchTimePointKeyStem + "log10 lower bound"] = data_summary[last_searchTimePointKeyStem_recorded + "log10 lower bound"]
                                data_summary[newSearchTimePointKeyStem + "ln upper bound"] = data_summary[last_searchTimePointKeyStem_recorded + "ln upper bound"]
                                data_summary[newSearchTimePointKeyStem + "log10 upper bound"] = data_summary[last_searchTimePointKeyStem_recorded + "log10 upper bound"]
                            newSearchTimePointsFinalizedIdx.append(i)
                    reversed_newSearchTimePointsRecordedIdx = reversed(newSearchTimePointsFinalizedIdx)
                    for idxToDel in reversed_newSearchTimePointsRecordedIdx:
                        del timepointsLeftToRecord[idxToDel]
                
                if last_searchTimePointKeyStem_recorded != None:
                    for tp in timepointsLeftToRecord:
                        searchTimePointKeyStem = "search timepoint (" + str(tp) + " sec): "
                        data_summary[searchTimePointKeyStem + "time"] = data_summary[last_searchTimePointKeyStem_recorded + "time"]
                        data_summary[searchTimePointKeyStem + "ln lower bound"] = data_summary[last_searchTimePointKeyStem_recorded + "ln lower bound"]
                        data_summary[searchTimePointKeyStem + "log10 lower bound"] = data_summary[last_searchTimePointKeyStem_recorded + "log10 lower bound"]
                        data_summary[searchTimePointKeyStem + "ln upper bound"] = data_summary[last_searchTimePointKeyStem_recorded + "ln upper bound"]
                        data_summary[searchTimePointKeyStem + "log10 upper bound"] = data_summary[last_searchTimePointKeyStem_recorded + "log10 upper bound"]                    
                
                finalSearchTimePointKeyStem = "final search timepoint: "
                if finalSearchLineData != None:
                    data_summary[finalSearchTimePointKeyStem + "time"] = finalSearchLineData["time"]
                    data_summary[finalSearchTimePointKeyStem + "ln lower bound"] = finalSearchLineData["log lower bound"]
                    data_summary[finalSearchTimePointKeyStem + "log10 lower bound"] = str(float(finalSearchLineData["log lower bound"])/math.log(10))
                    data_summary[finalSearchTimePointKeyStem + "ln upper bound"] = finalSearchLineData["log upper bound"]
                    if finalSearchLineData["log upper bound"] != "":
                        data_summary[finalSearchTimePointKeyStem + "log10 upper bound"] = str(float(finalSearchLineData["log upper bound"])/math.log(10))
                    else:
                        data_summary[finalSearchTimePointKeyStem + "log10 upper bound"] = ""
                else:
                    data_summary[finalSearchTimePointKeyStem + "time"] = ""
                    data_summary[finalSearchTimePointKeyStem + "ln lower bound"] = ""
                    data_summary[finalSearchTimePointKeyStem + "log10 lower bound"] = ""
                    data_summary[finalSearchTimePointKeyStem + "ln upper bound"] = ""
                    data_summary[finalSearchTimePointKeyStem + "log10 upper bound"] = ""	

                if matchFound == False:
                    break; # reached EOF

            
            # FINAL SUMMARY
            while(matchFound==True):
                prevLine, extractedLine, matchFound, match, numLinesReadIn = \
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

    # extract information from stderr
    if stderr_file_Path:
        data_summary["stderr file path"] = str(stderr_file_Path.relative_to(root));
        with stderr_file_Path.open('r') as stderr_file:
            for i, line in enumerate(stderr_file):
                data_summary["error line " + str(i)] = line.strip();

    return data_summary;