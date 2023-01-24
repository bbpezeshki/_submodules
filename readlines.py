

# reads a file line by line, stopping upon finding a given string match to the line

# returns
#   prevLine = the previous line read in from the file prior to finding a line match
#   currLine = the most recent line read in from the file and that matches the line-matching criteria or is the line corresponding to _maxNumLines (None corresponds to EOF being reached without reaching either condition)
#   matchFound = currLine matches one of the matching criteria (excluding _maxNumLines)
#   match = pair: ( <string> match_type, <int> match_key_idx )
#   numLinesReadIn = the number of lines read in (0 = file was already at EOF)

# params
#   _startswith: list of strings to match to beginning of a line
#   _endswith:   list of strings to match to the end of a line
#   _equals:     list of strings to match line to
#   _contains:   list of substring to find match with within line
#   _strip:      when looking for line matches, compare to the stripped line?
#   _prevLine:   the last known line read in from the file
def readLinesUntil(_fin, _startswith=None, _endswith=None, _equals=None, _contains=None, _maxNumLines=None, _strip=False, _returnstripped=None,_prevLine=None):
    fin = _fin

    # unless specified, the returned lines "strippedness" will correspond to how user asks for lines to be compared
    if _returnstripped==None:
        _returnstripped = _strip

    assert(any([_startswith != None, _endswith != None, _equals != None, _contains!=None, _maxNumLines != None])) # make sure there is a stop condition given

    # create working copy of match lists
    startswith = None
    endswith = None
    equals = None
    contains = None
    if _startswith != None:
        if type(_startswith)!=list:
            _startswith = [_startswith]
        startswith = _startswith.copy()
        # print(startswith)
    if _endswith != None:
        if type(_endswith)!=list:
            _endswith = [_endswith]
        endswith = _endswith.copy()
    if equals != None:
        if type(_equals)!=list:
            _equals = [_equals]
        equals = _equals.copy()
    if _contains != None:
        if type(_contains)!=list:
            _contains = [_contains]
        contains = _contains.copy()

    if _strip:
        if startswith != None:
            for i in range(len(startswith)):
                startswith[i] = startswith[i].lstrip()
                # print(startswith)
        if endswith != None:
            for i in range(len(endswith)):
                endswith[i] = endswith[i].rstrip()
        if equals != None:
            for i in range(len(equals)):
                equals[i] = equals[i].strip()
        if contains != None:
            for i in range(len(contains)):
                contains[i] = contains[i].strip()

    maxNumLines = None
    if _maxNumLines != None:
        maxNumLines = int(_maxNumLines)
        assert(maxNumLines > 0)

    numLinesReadIn = 0
    prevLine = None
    currLine = _prevLine
    matchFound = False
    match = None
    maxNumLinesReachedWithoutMatch = False
    for line in fin:
        numLinesReadIn += 1;
        prevLine = currLine
        currLine = line
        compareLine = line
        if _strip:
            compareLine = compareLine.strip()
        if startswith != None:
            for i, matchKey in enumerate(startswith):
                # print(matchKey)
                # print(compareLine)
                if compareLine.startswith(matchKey):
                    matchFound = True
                    match = ("_startswith", i,)
                    break;
            if matchFound == True:
                break
        if endswith != None:
            for i, matchKey in enumerate(endswith):
                if compareLine.endswith(matchKey):
                    matchFound = True
                    match = ("_endswith", i,)
                    break;
            if matchFound == True:
                break
        if equals != None:
            for i, matchKey in enumerate(equals):
                if compareLine == matchKey:
                    matchFound = True
                    match = ("_equals", i,)
                    break;
            if matchFound == True:
                break
        if contains != None:
            for i, matchKey in enumerate(contains):
                if matchKey in compareLine:
                    matchFound = True
                    match = ("_contains", i,)
                    break;
            if matchFound == True:
                break
        if numLinesReadIn == maxNumLines:
            maxNumLinesReachedWithoutMatch = True
            break;

    # if read in at least one line until maxNumLines and no match was found, simply return lines as is
    if maxNumLinesReachedWithoutMatch:
        pass;
    # if read lines until EOF, but no match was found, advance lines to having prevLine hold the last line, and currLine = None
    # (if file was already at EOF, effectively keeps prevLine as the passed in _prevLine, and currLine as None)
    elif not matchFound:
        prevLine = currLine
        currLine = None
    # strip returned lines if requested
    if _returnstripped:
        if currLine != None:
            currLine = currLine.strip()
        if prevLine != None:
            prevLine = prevLine.strip()
    
    return prevLine, currLine, matchFound, match, numLinesReadIn
    # returns
    #   prevLine = the previous line read in from the file prior to finding a line match
    #   currLine = the most recent line read in from the file and that matches the line-matching criteria or is the line corresponding to _maxNumLines (None corresponds to EOF being reached without reaching either condition)
    #   matchFound = currLine matches one of the matching criteria (excluding _maxNumLines)
    #   match = pair: ( <string> match_type, <int> match_key_idx )
    #   numLinesReadIn = the number of lines read in (0 = file was already at EOF)