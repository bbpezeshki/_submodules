from pathlib import Path
import csv

def loadReferenceZValues(refZValCSVFile=None, size=None):
    # for version compatibility
    if refZValCSVFile == None:
        if size == None or size.upper() == "SMALL":
            refZValCSVFile = "/home/bbpezeshki/VSCode/haplo1/ProblemDomains/TaskBased/Z/exactZvalues.csv"
        elif size.upper() == "LARGE":
            refZValCSVFile = "/home/bbpezeshki/VSCode/haplo1/ProblemDomains/TaskBased/Z/estimatedZvalues_byAverage.csv"
        else:
            assert(False)
    else:
        assert(size==None)

    refZValCSVFile = Path(refZValCSVFile)
    refZVals = {}
    with refZValCSVFile.open('r') as fin:
        dict_reader = csv.DictReader(fin, fieldnames=["problem", "refZVal"])
        for entry in dict_reader:
            assert(entry["problem"] not in refZVals)
            refZVals[entry["problem"]] = float(entry["refZVal"])
    if not refZVals:
        refZvals = None
    return refZVals


    