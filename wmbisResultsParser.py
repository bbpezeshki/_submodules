from pathlib import Path
from collections import OrderedDict
from collections import defaultdict
from readlines import *
import math
import numpy as np

INF = float("inf")
NINF = float("-inf")

def formatOptions(options):
    if options != None:
        assert(isinstance(options, dict))
        options = defaultdict(lambda: None, options)
    else:
        options = defaultdict(lambda: None)
    return options

def strip_and_split(line, split_on=None):
    tokens = None;
    if split_on:
        tokens = [t.strip() for t in line.split(split_on)];
    else:
        tokens = line.split();
    return tokens;



def process_stdout_problemName_line(line):
    
    # Reading model file: /home/pezeshkb/ProblemDomains/TaskBased/Z/DBN/rbm_20/rbm_20.uai
    
    line_tokens = strip_and_split(line, split_on=":")
    assert(line_tokens[0] == "Reading model file")
    problemFilePath = Path(line_tokens[1])
    problemName = problemFilePath.name.removesuffix(".uai")

    return problemName


def process_stdout_task_line(line):
    
    #Task is PR

    task_line_tokens = strip_and_split(line, split_on="is")
    assert(task_line_tokens[0] == "Task")
    
    task = task_line_tokens[1];

    return task;


def process_stdout_bound_line(line):
    
    # [0.00188303] :     196.23 , 196.23

    bound_line_tokens = strip_and_split(line, split_on=":")
    assert(len(bound_line_tokens)==2)
    preTime = float(bound_line_tokens[0].strip("[]"))
    measurement_tokens = strip_and_split(bound_line_tokens[1], split_on=",")
    assert(len(measurement_tokens)==2)
    ln_UB = float(measurement_tokens[0])
    
    return preTime, ln_UB


def process_stdout_sample_line(line):
    
    # [0.00618291] :    196.436 >    72.0158 >       -inf

    sample_line_tokens = strip_and_split(line, split_on=":")
    assert(len(sample_line_tokens)==2)
    time = float(sample_line_tokens[0].strip("[]"))
    measurement_tokens = strip_and_split(sample_line_tokens[1], split_on=">")
    assert(len(measurement_tokens)==3)
    ln_UB = float(measurement_tokens[0])
    lnZ_hat = float(measurement_tokens[1])
    
    return time, ln_UB, lnZ_hat



def update_data_summary_with_z_estimate_and_error(problemName, ln_z_hat, data_summary, exactRefZVals, estRefZVals):
    log10Zhat = ln_z_hat/math.log(10,math.exp(1));

    estZ_log10 = None
    if estRefZVals and problemName in estRefZVals:
        estZ_log10 = estRefZVals[problemName]
        data_summary["Reference Z Value (log10)"] = estZ_log10;
        log10_est_err = log10Zhat - estZ_log10
        data_summary["Estimated Error (log10)"] = log10_est_err;
        data_summary["Estimated Absolute Error (log10)"] = abs(log10_est_err);

    exactZ_log10 = None
    if exactRefZVals and problemName in exactRefZVals:
        exactZ_log10 = exactRefZVals[problemName]
        data_summary["Exact Z Value (log10)"] = exactZ_log10;
        log10_err = log10Zhat - exactZ_log10
        data_summary["Error (log10)"] = log10_err;
        data_summary["Absolute Error (log10)"] = abs(log10_err);
        data_summary["Reference Z Value (log10)"] = exactZ_log10;
        data_summary["Estimated Error (log10)"] = log10_err;
        data_summary["Estimated Absolute Error (log10)"] = abs(log10_err);

    if estRefZVals and problemName in estRefZVals:
        estZ_ln = estZ_log10/math.log(math.exp(1),10);
        data_summary["Reference Z Value (ln)"] = estZ_ln;
        ln_est_err = ln_z_hat - estZ_ln
        data_summary["Estimated Error (ln)"] = ln_est_err;
        data_summary["Estimated Absolute Error (ln)"] = abs(ln_est_err);

    if exactRefZVals and problemName in exactRefZVals:
        exactZ_ln = exactZ_log10/math.log(math.exp(1),10);
        data_summary["Exact Z Value (ln)"] = exactZ_ln;
        ln_err = ln_z_hat - exactZ_ln
        data_summary["Error (ln)"] = ln_err;
        data_summary["Absolute Error (ln)"] = abs(ln_err);
        data_summary["Reference Z Value (ln)"] = exactZ_ln;
        data_summary["Estimated Error (ln)"] = ln_err;
        data_summary["Estimated Absolute Error (ln)"] = exactZ_ln;

    return data_summary
    


def summarizeData(experiment_files_by_type_Dict, options=None, root=Path("")):
    options = formatOptions(options)
    assert(options["timelimit"] != None), "must include option to auto-extract time limit '--auto-extract-timelimit'"
    exactRefZVals = options["exactRefZVals"]
    estRefZVals = options["estRefZVals"]
    if "stdout" not in experiment_files_by_type_Dict:
        return None;
    data_summary = OrderedDict()
    stdout_file_Path = experiment_files_by_type_Dict["stdout"];
    stderr_file_Path = None
    if "stderr" in experiment_files_by_type_Dict:
        stderr_file_Path = experiment_files_by_type_Dict["stderr"];

    # extract informatino from stdout
    # data_summary["stdout file path"] = str(stdout_file_Path.relative_to(root));
    data_summary["stdout file path"] = str(stdout_file_Path.absolute());
    with stdout_file_Path.open('r') as stdout_fin:
        for i in range(1):

            # Extract problem name (first line)
            readLines = readLinesUntil(stdout_fin, _startswith="");
            line = readLines[CURR_LINE]
            problemName = process_stdout_problemName_line(line)
            if problemName == None:
                break;
            data_summary["Problem"] = problemName
            data_summary["Algorithm"] = "WMB-IS"

            # Extract Task
            readLines = readLinesUntil(stdout_fin, _startswith=["Task is"], _strip=True)
            if readLines[MATCH_FOUND]==False:
                break;
            line = readLines[CURR_LINE]	
            task = process_stdout_task_line(line)
            data_summary["Task"] = task
            
            # Extract ln WMB bound
            readLines = readLinesUntil(stdout_fin, _startswith=["["], _strip=True)
            if readLines[MATCH_FOUND]==False:
                break;
            line = readLines[CURR_LINE]	
            # print()
            # print(readLines[PREV_LINE])
            # print(readLines[CURR_LINE])
            preTime, lnMBEBound = process_stdout_bound_line(line)
            data_summary["Preprocessing Time"] = preTime
            data_summary["WMB ln Bound"] = lnMBEBound
            log10MBEBound = lnMBEBound/math.log(10,math.exp(1));
            data_summary["WMB Log10 Bound"] = log10MBEBound

            # Process time limit
            timelimit = options["timelimit"]
            data_summary["Time Limit"] = timelimit

            # Extract final sample line info
            while readLines[MATCH_FOUND]==True:
                readLines = readLinesUntil(stdout_fin, _startswith=["["], _strip=True, _prevLine=readLines[CURR_LINE])
                # print()
                # print(readLines[PREV_LINE])
                # print(readLines[CURR_LINE])
            line = readLines[PREV_LINE]	
            # print()
            # print(readLines[PREV_LINE])
            # print(readLines[CURR_LINE])
            # print(problemName)
            if line == "==== Beginning WMB importance sampling ====":
                break;
            time, ln_UB, lnZ_hat = process_stdout_sample_line(line)
            assert(time < 1.05 * float(timelimit))


            data_summary["Elapsed Time"] = time
            data_summary["Tightened WMB ln Bound"] = ln_UB
            log10UB = ln_UB/math.log(10,math.exp(1));
            data_summary["Tightened WMB Log10 Bound"] = log10UB
            if (lnZ_hat == None) or (not math.isfinite(lnZ_hat)):
                update_data_summary_with_z_estimate_and_error(problemName, ln_UB, data_summary, exactRefZVals, estRefZVals)
            else:
                data_summary["ln Z hat"] = lnZ_hat
                log10Z_hat = lnZ_hat/math.log(10,math.exp(1));
                data_summary["log10 Z hat"] = log10Z_hat
                update_data_summary_with_z_estimate_and_error(problemName, lnZ_hat, data_summary, exactRefZVals, estRefZVals)

    
    # extract information from stderr
    if stderr_file_Path != None:
        # data_summary["stderr file path"] = str(stderr_file_Path.relative_to(root));
        data_summary["stderr file path"] = str(stderr_file_Path.absolute());
        with stderr_file_Path.open('r') as stderr_file:
            for i, line in enumerate(stderr_file):
                data_summary["error line " + str(i)] = line.strip();


    return data_summary;


