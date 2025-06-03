from pathlib import Path
from argparse import ArgumentParser, Namespace
from datetime import datetime
import csv

# parser = ArgumentParser()
# parser.add_argument("--csvFile", required=True, help="csvFiles to process")
# parser.add_argument("--columns-to-keep", default=None, nargs="+", help="csv columns to keep")
# parser.add_argument("--columns-to-delete", default=None, nargs="+", help="csv columns to remove")
# parser.add_argument("--column-renamings", default=[], nargs="+", help='syntax: "time: 20sec" "20sec" "time: 30sec" "30sec"')

# args = parser.parse_args()

def processCsv(args, write=True):

    if type(args) == dict:
        args = Namespace(**args)

    if not hasattr(args, 'columns_to_keep'):
        args.columns_to_keep = None
    if not hasattr(args, 'columns_to_delete'):
        args.columns_to_delete = None
    if not hasattr(args, 'column_renamings'):
        args.column_renamings = []

    csvFile = Path(args.csvFile)
    csvRows = None
    with csvFile.open('r') as fin:
        csvReader = csv.DictReader(fin)
        csvRows = list(csvReader)
    rowOneKeysList = list(csvRows[0].keys())
    rowOneKeysSet = set(rowOneKeysList)
    assert(all(rowOneKeysSet==set(row.keys()) for row in csvRows))
    assert("restkey" not in rowOneKeysSet)

    assert(args.columns_to_keep==None or args.columns_to_delete==None)

    columnsToKeepList = args.columns_to_keep
    columnsToKeepSet = None
    if columnsToKeepList == None:
        if args.columns_to_delete == None:
            columnsToDelete = set()
        else:
            columnsToDelete = set(args.columns_to_delete)
        assert(columnsToDelete.issubset(rowOneKeysSet))
        columnsToKeepList = [k for k in rowOneKeysList if k not in columnsToDelete]
        columnsToKeepSet = set(columnsToKeepList)
    else:
        columnsToKeepSet = set(columnsToKeepList)
        assert(columnsToKeepSet.issubset(rowOneKeysSet))

    columnRenamingsRawList = args.column_renamings
    assert(len(columnRenamingsRawList) % 2 == 0)
    columnRenamingsKeys = columnRenamingsRawList[0::2]
    columnRenamingsVals = columnRenamingsRawList[1::2]
    assert(len(columnRenamingsKeys) == len(columnRenamingsVals))
    assert(all(k in rowOneKeysSet for k in columnRenamingsKeys))
    assert(not any(v in rowOneKeysSet for v in columnRenamingsVals))
    columnRenamingsDict = dict(zip(columnRenamingsKeys, columnRenamingsVals))


    # update column names
    for key in columnRenamingsDict:
        if key in columnsToKeepSet:
            columnsToKeepSet.remove(key)
            columnsToKeepSet.add(columnRenamingsDict[key])
            idx = columnsToKeepList.index(key)
            columnsToKeepList[idx] = columnRenamingsDict[key]
    for row in csvRows:
        for key in columnRenamingsDict:
            row[columnRenamingsDict[key]] = row.pop(key)

    if write == True:
        writeCsv(csvFile, csvRows, columnsToKeepList)


    return csvRows, columnsToKeepList, columnsToKeepSet, csvFile, args

def writeCsv(csvFile, csvRows, columnsToKeepList, indicateProcessed=True): #csvFile is the original csvFile Path()
    csvFile = Path(csvFile)
    current_time = datetime.now()
    if indicateProcessed==True:
        newCsvFilename = csvFile.stem + "__processed-" + current_time.strftime("%Y-%m-%d-%H%M") + csvFile.suffix
        newCsvFile = Path(newCsvFilename)
    else:
        newCsvFile = csvFile
    with newCsvFile.open('w') as fout:
        csvDictWriter = csv.DictWriter(fout, fieldnames=columnsToKeepList, extrasaction="ignore")
        csvDictWriter.writeheader()
        csvDictWriter.writerows(csvRows)

if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument("--csvFile", required=True, help="csvFiles to process")
    parser.add_argument("--columns-to-keep", default=None, nargs="+", help="csv columns to keep")
    parser.add_argument("--columns-to-delete", default=None, nargs="+", help="csv columns to remove")
    parser.add_argument("--column-renamings", default=[], nargs="+", help='syntax: "time: 20sec" "20sec" "time: 30sec" "30sec"')

    args = parser.parse_args()
    
    processCsv(args)