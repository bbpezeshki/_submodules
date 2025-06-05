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
	stripped_line = line.strip()

	stripped_line = stripped_line.removesuffix(".PR")
	stripped_line = stripped_line.removesuffix(".MAR")
	stripped_line = stripped_line.removesuffix(".uai")

	problemName = stripped_line

	return problemName


def process_stdout_totalTime_line(line):
	totalTime_line_tokens = strip_and_split(line, split_on="=")
	assert(totalTime_line_tokens[0] == "Total time")
	
	totalTime = int(totalTime_line_tokens[1]);

	return totalTime;


def process_stdout_iBound_line(line):
	task_line_tokens = strip_and_split(line, split_on="=")
	assert(task_line_tokens[0] == "i-bound")
	
	iB = int(task_line_tokens[1]);

	return iB;


def process_output_task_line(line):
	if line==None or line.strip()=="":
		return None
	
	task_line_tokens = strip_and_split(line);

	if len(task_line_tokens) != 1:
		return None;

	if (task_line_tokens[0] != "PR" and task_line_tokens[0] != "MAR"):
		return None
	
	task = task_line_tokens[0];

	return task;


def process_output_z_estimate_line(line):
	if line==None or line.strip()=="":
		return None;
	log10_Z_line_tokens = strip_and_split(line);

	if len(log10_Z_line_tokens) != 1:
		return None;

	processed_z_estimate = float(log10_Z_line_tokens[0])
	
	return processed_z_estimate


def update_data_summary_with_z_estimate_and_error(problemName, log10_z_hat, data_summary, exactRefZVals, estRefZVals):
	lnZhat = log10_z_hat/math.log(math.exp(1),10);

	estZ_log10 = None
	if estRefZVals and problemName in estRefZVals:
		estZ_log10 = estRefZVals[problemName]
		data_summary["Reference Z Value (log10)"] = estZ_log10;
		log10_est_err = log10_z_hat - estZ_log10
		data_summary["Estimated Error (log10)"] = log10_est_err;
		data_summary["Estimated Absolute Error (log10)"] = abs(log10_est_err);

	exactZ_log10 = None
	if exactRefZVals and problemName in exactRefZVals:
		exactZ_log10 = exactRefZVals[problemName]
		data_summary["Exact Z Value (log10)"] = exactZ_log10;
		log10_err = log10_z_hat - exactZ_log10
		data_summary["Error (log10)"] = log10_err;
		data_summary["Absolute Error (log10)"] = abs(log10_err);
		data_summary["Reference Z Value (log10)"] = exactZ_log10;
		data_summary["Estimated Error (log10)"] = log10_err;
		data_summary["Estimated Absolute Error (log10)"] = abs(log10_err);

	if estRefZVals and problemName in estRefZVals:
		estZ_ln = estZ_log10/math.log(math.exp(1),10);
		data_summary["Reference Z Value (ln)"] = estZ_ln;
		ln_est_err = lnZhat - estZ_ln
		data_summary["Estimated Error (ln)"] = ln_est_err;
		data_summary["Estimated Absolute Error (ln)"] = abs(ln_est_err);

	if exactRefZVals and problemName in exactRefZVals:
		exactZ_ln = exactZ_log10/math.log(math.exp(1),10);
		data_summary["Exact Z Value (ln)"] = exactZ_ln;
		ln_err = lnZhat - exactZ_ln
		data_summary["Error (ln)"] = ln_err;
		data_summary["Absolute Error (ln)"] = abs(ln_err);
		data_summary["Reference Z Value (ln)"] = exactZ_ln;
		data_summary["Estimated Error (ln)"] = ln_err;
		data_summary["Estimated Absolute Error (ln)"] = exactZ_ln;

	return data_summary
	


def summarizeData(experiment_files_by_type_Dict, options=None, root=Path("")):
	options = formatOptions(options)
	exactRefZVals = options["exactRefZVals"]
	estRefZVals = options["estRefZVals"]
	log10MBEBounds = options["log10MBEBounds"]
	if "output" not in experiment_files_by_type_Dict:
		return None;
	if "stdout" not in experiment_files_by_type_Dict:
		return None;
	data_summary = OrderedDict()
	stdout_file_Path = experiment_files_by_type_Dict["stdout"];
	output_file_Path = experiment_files_by_type_Dict["output"];
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
			problem = process_stdout_problemName_line(line)
			if problem == None:
				break;
			data_summary["Problem"] = problem
			data_summary["Algorithm"] = "IJGP-SS"

			# Extract Total Time
			readLines = readLinesUntil(stdout_fin, _startswith=["Total time ="], _strip=True)
			if readLines[MATCH_FOUND]==False:
				break;
			line = readLines[CURR_LINE]	
			totalTime = process_stdout_totalTime_line(line)
			data_summary["Total time"] = totalTime

			# Extract i-bound
			readLines = readLinesUntil(stdout_fin, _startswith=["i-bound ="], _strip=True)
			if readLines[MATCH_FOUND]==False:
				break;
			line = readLines[CURR_LINE]	
			iB = process_stdout_iBound_line(line)
			data_summary["i-bound"] = iB
	


	# extract information from output file
	data_summary["output file path"] = str(output_file_Path.relative_to(root));
	configs_without_MBELogBounds = set()
	with output_file_Path.open('r') as output_fin:
		for i in range(1):

			# Get First Line (Task) Tokens
			readLines = readLinesUntil(output_fin, _startswith="");
			line = readLines[CURR_LINE]
			task = process_output_task_line(line)
			if task == None:
				break;
			data_summary["Task"] = task

			# Get estimated Z value
			readLines = readLinesUntil(output_fin, _startswith="");
			line = readLines[CURR_LINE]
			log10_Zhat = process_output_z_estimate_line(line)

			problemName = data_summary["Problem"]
			iB = data_summary["i-bound"]
			config = (problemName, iB)
			try:
				log10MBEBound = log10MBEBounds[config]
			except:
				configs_without_MBELogBounds.add(config)
				log10MBEBound = float("nan")
			ln10MBEBound = log10MBEBound/math.log(math.exp(1),10);
			data_summary["WMB Log10 Bound"] = log10MBEBound
			data_summary["WMB ln Bound"] = ln10MBEBound
			if (log10_Zhat == None) or (not math.isfinite(log10_Zhat)):
				update_data_summary_with_z_estimate_and_error(problemName, log10MBEBound, data_summary, exactRefZVals, estRefZVals)
			else:
				data_summary["log10 Z hat"] = log10_Zhat
				data_summary["ln Z hat"] = log10_Zhat/math.log(math.exp(1),10);
				update_data_summary_with_z_estimate_and_error(problemName, log10_Zhat, data_summary, exactRefZVals, estRefZVals)

	if len(configs_without_MBELogBounds) > 0:
		print('NO PRE-STORED MBE LOG10 BOUND:', end="")
		for config in configs_without_MBELogBounds:
			print('\t',config)

	return data_summary;


