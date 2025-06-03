from pathlib import Path
import csv

def loadMBELog10Bounds(mbeLog10BoundsFile=None):
    # for version compatibility
    if mbeLog10BoundsFile == None:
        mbeLog10BoundsFile = "/home/bbpezeshki/VSCode/haplo1/ProblemDomains/TaskBased/Z/MBE_log10Bounds.csv"

    mbeLog10BoundsFile = Path(mbeLog10BoundsFile)
    MBELog10Bounds = {}
    with mbeLog10BoundsFile.open('r') as fin:
        dict_reader = csv.DictReader(fin)
        for entry in dict_reader:
            config = (entry["problem"], int(entry["iB"]))
            assert(config not in MBELog10Bounds)
            MBELog10Bounds[config] = float(entry["MBE Log Bound"])
    
    if not MBELog10Bounds:
        MBELog10Bounds = None

    return MBELog10Bounds


    