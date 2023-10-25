from pathlib import Path
import csv

def loadReferenceZValues(refZValCSVFile = "/home/bbpezeshki/VSCode/haplo1/ProblemDomains/TaskBased/Z/exactZvalues.csv"):
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


    