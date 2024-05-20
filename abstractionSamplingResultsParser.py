from pathlib import Path
from collections import OrderedDict
from collections import defaultdict
import referenceZValuesLoader
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

def readSampleLines_until_last_non_empty_line(file, timelimit=None):
	all_lines = []
	for line in file:
		line = line.strip();
		if line:
			if timelimit != None:
				time = parseTimeFromSampleLine(line)
				if time > timelimit:
					break;
			all_lines.append(line)
		else:
			break;
	return all_lines;

def read_last_sample_line(file, timelimit=None):
	final_line = None
	for line in file:
		line = line.strip();
		if line:
			if timelimit != None:
				time = parseTimeFromSampleLine(line)
				if time > timelimit:
					break;
			final_line = line
		else:
			break;
	return final_line;


def strip_and_split(line, split_on=None):
	tokens = None;
	line = line.strip();
	if split_on:
		tokens = line.split(split_on);
	else:
		tokens = line.split();
	return tokens;

def extractTimelimitFromOutputFilePath(outfilepath):
	return int(outfilepath.split("-t-")[-1].split("-")[0].split(".")[0])
	
def parseTimeFromSampleLine(line):
	line_tokens = strip_and_split(line);
	time = float(get_time_from_final_sample_line_tokens(line_tokens))
	return time
		
def parseSampleLine(line, problemName=None, exactRefZVals=None, estRefZVals=None, log10MBEBound=None):
	log10MBEBound = float(log10MBEBound)
	lnMBEBound = log10MBEBound/math.log(math.exp(1),10)

	parsedSampleLine = {}

	line_tokens = strip_and_split(line);

	# Number of Samples
	number_of_samples = get_number_of_samples_from_final_sample_line_tokens(line_tokens);
	parsedSampleLine["Number of Samples"] = int(number_of_samples);

	Z_estimate_log10 = float(get_final_Z_estimate_from_final_sample_line_tokens(line_tokens));
	parsedSampleLine["Z Estimate (log10)"] = Z_estimate_log10;
	useMBEBoundAsEstimate = (Z_estimate_log10 == NINF and log10MBEBound != None and log10MBEBound != INF)

	estZ_log10 = None
	if estRefZVals and problemName in estRefZVals:
		estZ_log10 = estRefZVals[problemName]
		parsedSampleLine["Reference Z Value (log10)"] = estZ_log10;
		if useMBEBoundAsEstimate:
			log10_est_err = log10MBEBound - estZ_log10
		else:
			log10_est_err = Z_estimate_log10 - estZ_log10
		parsedSampleLine["Estimated Error (log10)"] = log10_est_err;
		parsedSampleLine["Estimated Absolute Error (log10)"] = abs(log10_est_err);
	else:
		parsedSampleLine["Reference Z Value (log10)"] = "";
		parsedSampleLine["Estimated Error (log10)"] = "";
		parsedSampleLine["Estimated Absolute Error (log10)"] = "";

	exactZ_log10 = None
	if exactRefZVals and problemName in exactRefZVals:
		exactZ_log10 = exactRefZVals[problemName]
		parsedSampleLine["Exact Z Value (log10)"] = exactZ_log10;
		if useMBEBoundAsEstimate:
			log10_err = log10MBEBound - exactZ_log10
		else:
			log10_err = Z_estimate_log10 - exactZ_log10
		parsedSampleLine["Error (log10)"] = log10_err;
		parsedSampleLine["Absolute Error (log10)"] = abs(log10_err);
		parsedSampleLine["Reference Z Value (log10)"] = exactZ_log10;
		parsedSampleLine["Estimated Error (log10)"] = log10_err;
		parsedSampleLine["Estimated Absolute Error (log10)"] = abs(log10_err);
	else:
		parsedSampleLine["Exact Z Value (log10)"] = "";
		parsedSampleLine["Error (log10)"] = "";
		parsedSampleLine["Absolute Error (log10)"] = "";

	Z_estimate_ln = float(Z_estimate_log10)/math.log(math.exp(1),10);
	parsedSampleLine["Z Estimate (ln)"] = Z_estimate_ln;

	if estRefZVals and problemName in estRefZVals:
		estZ_ln = estZ_log10/math.log(math.exp(1),10);
		parsedSampleLine["Reference Z Value (ln)"] = estZ_ln;
		if useMBEBoundAsEstimate:
			ln_est_err = lnMBEBound - estZ_ln
		else:
			ln_est_err = Z_estimate_ln - estZ_ln
		parsedSampleLine["Estimated Error (ln)"] = ln_est_err;
		parsedSampleLine["Estimated Absolute Error (ln)"] = abs(ln_est_err);
	else:
		parsedSampleLine["Reference Z Value (ln)"] = "";
		parsedSampleLine["Estimated Error (ln)"] = "";
		parsedSampleLine["Estimated Absolute Error (ln)"] = "";

	if exactRefZVals and problemName in exactRefZVals:
		exactZ_ln = exactZ_log10/math.log(math.exp(1),10);
		parsedSampleLine["Exact Z Value (ln)"] = exactZ_ln;
		if useMBEBoundAsEstimate:
			ln_err = lnMBEBound - exactZ_ln
		else:
			ln_err = Z_estimate_ln - exactZ_ln
		parsedSampleLine["Error (ln)"] = ln_err;
		parsedSampleLine["Absolute Error (ln)"] = abs(ln_err);
		parsedSampleLine["Reference Z Value (ln)"] = exactZ_ln;
		parsedSampleLine["Estimated Error (ln)"] = ln_err;
		parsedSampleLine["Estimated Absolute Error (ln)"] = exactZ_ln;
	else:
		parsedSampleLine["Exact Z Value (ln)"] = "";
		parsedSampleLine["Error (ln)"] = "";
		parsedSampleLine["Absolute Error (ln)"] = "";

	# Number of Nodes in Final Sampling Tree
	nodes_per_probe = get_number_of_nodes_in_final_sampling_tree_from_final_sample_line_tokens(line_tokens);
	parsedSampleLine["Average Number of Nodes Created Per Probe"] = int(nodes_per_probe);

	# Time
	time = get_time_from_final_sample_line_tokens(line_tokens);
	parsedSampleLine["Time"] = float(time);
	
	return parsedSampleLine



def get_problem_from_program_parameters_line_tokens(program_parameters_line_tokens):
	problemName = Path(program_parameters_line_tokens[0]).stem;
	return problemName;

def get_iB_from_program_parameters_line_tokens(program_parameters_line_tokens):
	iB = program_parameters_line_tokens[1];
	return iB;

def get_algorithm_from_program_parameters_line_tokens(program_parameters_line_tokens):
	alg = program_parameters_line_tokens[2];
	return alg;

def get_number_of_variables_from_program_parameters_line_tokens(program_parameters_line_tokens):
	number_of_variables = program_parameters_line_tokens[6];
	return number_of_variables;

def get_induced_width_from_program_parameters_line_tokens(program_parameters_line_tokens):
	width = program_parameters_line_tokens[7];
	return width;

def get_pseudotree_depth_from_program_parameters_line_tokens(program_parameters_line_tokens):
	depth = program_parameters_line_tokens[8];
	return depth;

def get_mbe_log_bound_from_program_parameters_line_tokens(program_parameters_line_tokens):
	mbe_log_bound = program_parameters_line_tokens[9];
	return mbe_log_bound;

def get_preprocessing_time_from_program_parameters_line_tokens(program_parameters_line_tokens):
	preprocessing_time = program_parameters_line_tokens[11];
	return preprocessing_time;

def get_number_of_samples_from_final_sample_line_tokens(final_sample_line_tokens):
	number_of_samples = final_sample_line_tokens[0];
	return number_of_samples;

def get_final_Z_estimate_from_final_sample_line_tokens(final_sample_line_tokens):
	final_Z_estimate = final_sample_line_tokens[2];
	return final_Z_estimate;

def get_number_of_nodes_in_final_sampling_tree_from_final_sample_line_tokens(final_sample_line_tokens):
	number_of_nodes_in_final_sampling_tree = final_sample_line_tokens[11];
	return number_of_nodes_in_final_sampling_tree;

def get_time_from_final_sample_line_tokens(final_sample_line_tokens):
	time = final_sample_line_tokens[9];
	return time;


def summarizeData(experiment_files_by_type_Dict, options=None, root=Path("")):
	options = formatOptions(options)
	exactRefZVals = options["exactRefZVals"]
	estRefZVals = options["estRefZVals"]
	if "output" not in experiment_files_by_type_Dict:
		return None;
	data_summary = OrderedDict()
	output_file_Path = experiment_files_by_type_Dict["output"];
	stderr_file_Path = None
	if "stderr" in experiment_files_by_type_Dict:
		stderr_file_Path = experiment_files_by_type_Dict["stderr"];

	# extract information from stdout
	data_summary["output file path"] = str(output_file_Path.relative_to(root));
	with output_file_Path.open('r') as output_file:
		for i in range(1):

			# Get First Line (Program Parameters) Tokens
			readLines = readLinesUntil(output_file, "");
			line = readLines[CURR_LINE]
			if line==None:
				break;
			program_parameters_line_tokens = strip_and_split(line);

			problemName = get_problem_from_program_parameters_line_tokens(program_parameters_line_tokens)
			data_summary["Problem"] = problemName

			iB = get_iB_from_program_parameters_line_tokens(program_parameters_line_tokens)
			data_summary["iB"] = iB

			alg = get_algorithm_from_program_parameters_line_tokens(program_parameters_line_tokens)
			data_summary["Algorithm"] = alg

			# Number of Variables (I believe this is before pre-processing!)
			number_of_variables = get_number_of_variables_from_program_parameters_line_tokens(program_parameters_line_tokens);
			data_summary["Number of Variables"] = number_of_variables;

			# Induced Width
			width = get_induced_width_from_program_parameters_line_tokens(program_parameters_line_tokens);
			data_summary["Induced Width"] = width;

			# Pseudotree Depth
			depth = get_pseudotree_depth_from_program_parameters_line_tokens(program_parameters_line_tokens);
			data_summary["Pseudotree Depth"] = depth;

			# MBE Log Bound
			mbe_log_bound = get_mbe_log_bound_from_program_parameters_line_tokens(program_parameters_line_tokens);
			data_summary["MBE Log Bound"] = mbe_log_bound;

			# Preprocessing Time
			preprocessing_time = get_preprocessing_time_from_program_parameters_line_tokens(program_parameters_line_tokens);
			data_summary["Preprocessing Time"] = preprocessing_time;


			# Read until final non-empty line that returns before time-limit
			try:
				timelimit = extractTimelimitFromOutputFilePath(data_summary["output file path"])
			except:
				timelimit = timelimit = options["timelimit"]
			data_summary["Time Limit"] = timelimit

			final_sample_line = read_last_sample_line(output_file, timelimit=timelimit);

			if not final_sample_line:
				log10MBEBound = float(mbe_log_bound)
				lnMBEBound = log10MBEBound/math.log(math.exp(1),10);

				estZ_log10 = None
				if estRefZVals and problemName in estRefZVals:
					estZ_log10 = estRefZVals[problemName]
					data_summary["Reference Z Value (log10)"] = estZ_log10;
					log10_est_err = log10MBEBound - estZ_log10
					data_summary["Estimated Error (log10)"] = log10_est_err;
					data_summary["Estimated Absolute Error (log10)"] = abs(log10_est_err);

				exactZ_log10 = None
				if exactRefZVals and problemName in exactRefZVals:
					exactZ_log10 = exactRefZVals[problemName]
					data_summary["Exact Z Value (log10)"] = exactZ_log10;
					log10_err = log10MBEBound - exactZ_log10
					data_summary["Error (log10)"] = log10_err;
					data_summary["Absolute Error (log10)"] = abs(log10_err);
					data_summary["Reference Z Value (log10)"] = exactZ_log10;
					data_summary["Estimated Error (log10)"] = log10_err;
					data_summary["Estimated Absolute Error (log10)"] = abs(log10_err);

				if estRefZVals and problemName in estRefZVals:
					estZ_ln = estZ_log10/math.log(math.exp(1),10);
					data_summary["Reference Z Value (ln)"] = estZ_ln;
					ln_est_err = lnMBEBound - estZ_ln
					data_summary["Estimated Error (ln)"] = ln_est_err;
					data_summary["Estimated Absolute Error (ln)"] = abs(ln_est_err);

				if exactRefZVals and problemName in exactRefZVals:
					exactZ_ln = exactZ_log10/math.log(math.exp(1),10);
					data_summary["Exact Z Value (ln)"] = exactZ_ln;
					ln_err = lnMBEBound - exactZ_ln
					data_summary["Error (ln)"] = ln_err;
					data_summary["Absolute Error (ln)"] = abs(ln_err);
					data_summary["Reference Z Value (ln)"] = exactZ_ln;
					data_summary["Estimated Error (ln)"] = ln_err;
					data_summary["Estimated Absolute Error (ln)"] = exactZ_ln;

				break;

			# # Final Z Estimate vs Reference
			# exactRefZVals = referenceZValuesLoader.loadReferenceZValues();
			# estRefZVals = referenceZValuesLoader.loadReferenceZValues(refZValCSVFile="/home/bbpezeshki/VSCode/haplo1/ProblemDomains/TaskBased/Z/estimatedZvalues_byAverage.csv")

			# Parse Sample Lines
			parsedFinalSampleLine = parseSampleLine(
				final_sample_line, 
				problemName=problemName, 
				exactRefZVals=exactRefZVals, 
				estRefZVals=estRefZVals,
				log10MBEBound=mbe_log_bound)
			data_summary["Number of Samples"] = parsedFinalSampleLine["Number of Samples"];

			data_summary["Z Estimate (log10)"] = parsedFinalSampleLine["Z Estimate (log10)"];
			data_summary["Exact Z Value (log10)"] = parsedFinalSampleLine["Exact Z Value (log10)"];
			data_summary["Error (log10)"] = parsedFinalSampleLine["Error (log10)"];
			data_summary["Absolute Error (log10)"] = parsedFinalSampleLine["Absolute Error (log10)"];
			data_summary["Reference Z Value (log10)"] = parsedFinalSampleLine["Reference Z Value (log10)"];
			data_summary["Estimated Error (log10)"] = parsedFinalSampleLine["Estimated Error (log10)"];
			data_summary["Estimated Absolute Error (log10)"] = parsedFinalSampleLine["Estimated Absolute Error (log10)"];

			data_summary["Z Estimate (ln)"] = parsedFinalSampleLine["Z Estimate (ln)"];
			data_summary["Exact Z Value (ln)"] = parsedFinalSampleLine["Exact Z Value (ln)"];
			data_summary["Error (ln)"] = parsedFinalSampleLine["Error (ln)"];
			data_summary["Absolute Error (ln)"] = parsedFinalSampleLine["Absolute Error (ln)"];
			data_summary["Reference Z Value (ln)"] = parsedFinalSampleLine["Reference Z Value (ln)"];
			data_summary["Estimated Error (ln)"] = parsedFinalSampleLine["Estimated Error (ln)"];
			data_summary["Estimated Absolute Error (ln)"] = parsedFinalSampleLine["Estimated Absolute Error (ln)"];

			data_summary["Average Number of Nodes Created Per Probe"] = parsedFinalSampleLine["Average Number of Nodes Created Per Probe"];

			data_summary["Time"] = parsedFinalSampleLine["Time"];



	# extract information from stderr
	if stderr_file_Path != None:
		data_summary["stderr file path"] = str(stderr_file_Path.relative_to(root));
		with stderr_file_Path.open('r') as stderr_file:
			for i, line in enumerate(stderr_file):
				data_summary["error line " + str(i)] = line.strip();

	return data_summary;



def summarizeDataForPlots(experiment_files_by_type_Dict, options=None, root=Path("")):
	options = formatOptions(options)
	if "output" not in experiment_files_by_type_Dict:
		return None;
	data_summary = OrderedDict()
	output_file_Path = experiment_files_by_type_Dict["output"];
	stderr_file_Path = None
	if "stderr" in experiment_files_by_type_Dict:
		stderr_file_Path = experiment_files_by_type_Dict["stderr"];

	parsedSampleLines = None
	# extract information from stdout
	data_summary["output file path"] = str(output_file_Path.relative_to(root));
	with output_file_Path.open('r') as output_file:
		for i in range(1):
			
			# Get First Line (Program Parameters) Tokens
			readLines = readLinesUntil(output_file, "");
			line = readLines[CURR_LINE]
			if line==None:
				break;
			program_parameters_line_tokens = strip_and_split(line);

			problemName = get_problem_from_program_parameters_line_tokens(program_parameters_line_tokens)
			data_summary["Problem"] = problemName

			iB = get_iB_from_program_parameters_line_tokens(program_parameters_line_tokens)
			data_summary["iB"] = iB

			alg = get_algorithm_from_program_parameters_line_tokens(program_parameters_line_tokens)
			data_summary["Algorithm"] = alg

			# Number of Variables (I believe this is before pre-processing!)
			number_of_variables = get_number_of_variables_from_program_parameters_line_tokens(program_parameters_line_tokens);
			data_summary["Number of Variables"] = number_of_variables;

			# Induced Width
			width = get_induced_width_from_program_parameters_line_tokens(program_parameters_line_tokens);
			data_summary["Induced Width"] = width;

			# Pseudotree Depth
			depth = get_pseudotree_depth_from_program_parameters_line_tokens(program_parameters_line_tokens);
			data_summary["Pseudotree Depth"] = depth;

			# MBE Log Bound
			mbe_log_bound = get_mbe_log_bound_from_program_parameters_line_tokens(program_parameters_line_tokens);
			data_summary["MBE Log Bound"] = mbe_log_bound;

			# Preprocessing Time
			preprocessing_time = get_preprocessing_time_from_program_parameters_line_tokens(program_parameters_line_tokens);
			data_summary["Preprocessing Time"] = preprocessing_time;


			# Read until final non-empty line that does not excede timelimit
			try:
				timelimit = extractTimelimitFromOutputFilePath(data_summary["output file path"])
			except:
				timelimit = timelimit = options["timelimit"]
			data_summary["Time Limit"] = timelimit
				
			all_sample_lines = readSampleLines_until_last_non_empty_line(output_file, timelimit=timelimit);

			if not all_sample_lines:
				log10MBEBound = float(mbe_log_bound)
				lnMBEBound = log10MBEBound/math.log(math.exp(1),10);
				
				estZ_log10 = None
				if estRefZVals and problemName in estRefZVals:
					estZ_log10 = estRefZVals[problemName]
					data_summary["Reference Z Value (log10)"] = estZ_log10;
					log10_est_err = log10MBEBound - estZ_log10
					data_summary["Estimated Error (log10)"] = log10_est_err;
					data_summary["Estimated Absolute Error (log10)"] = abs(log10_est_err);

				exactZ_log10 = None
				if exactRefZVals and problemName in exactRefZVals:
					exactZ_log10 = exactRefZVals[problemName]
					data_summary["Exact Z Value (log10)"] = exactZ_log10;
					log10_err = log10MBEBound - exactZ_log10
					data_summary["Error (log10)"] = log10_err;
					data_summary["Absolute Error (log10)"] = abs(log10_err);
					data_summary["Reference Z Value (log10)"] = exactZ_log10;
					data_summary["Estimated Error (log10)"] = log10_err;
					data_summary["Estimated Absolute Error (log10)"] = abs(log10_err);

				if estRefZVals and problemName in estRefZVals:
					estZ_ln = estZ_log10/math.log(math.exp(1),10);
					data_summary["Reference Z Value (ln)"] = estZ_ln;
					ln_est_err = lnMBEBound - estZ_ln
					data_summary["Estimated Error (ln)"] = ln_est_err;
					data_summary["Estimated Absolute Error (ln)"] = abs(ln_est_err);

				if exactRefZVals and problemName in exactRefZVals:
					exactZ_ln = exactZ_log10/math.log(math.exp(1),10);
					data_summary["Exact Z Value (ln)"] = exactZ_ln;
					ln_err = lnMBEBound - exactZ_ln
					data_summary["Error (ln)"] = ln_err;
					data_summary["Absolute Error (ln)"] = abs(ln_err);
					data_summary["Reference Z Value (ln)"] = exactZ_ln;
					data_summary["Estimated Error (ln)"] = ln_err;
					data_summary["Estimated Absolute Error (ln)"] = exactZ_ln;

				break;
			# print(all_sample_lines)

			# # Final Z Estimate vs Reference
			# exactRefZVals = referenceZValuesLoader.loadReferenceZValues();
			# estRefZVals = referenceZValuesLoader.loadReferenceZValues(refZValCSVFile="/home/bbpezeshki/VSCode/haplo1/ProblemDomains/TaskBased/Z/estimatedZvalues_byAverage.csv")

			# Parse Sample Lines
			parsedSampleLines = []
			for line in all_sample_lines:
				sampleSummary = {}
				parsedSampleLine = parseSampleLine(
					line, 
					problemName=problemName, 
					exactRefZVals=options["exactRefZVals"], 
					estRefZVals=options["estRefZVals"],
					log10MBEBound=mbe_log_bound)
				parsedSampleLines.append(parsedSampleLine)

			parsedFinalSampleLine = parsedSampleLines[-1]
			data_summary["Number of Samples"] = parsedFinalSampleLine["Number of Samples"];

			data_summary["Z Estimate (log10)"] = parsedFinalSampleLine["Z Estimate (log10)"];
			data_summary["Exact Z Value (log10)"] = parsedFinalSampleLine["Exact Z Value (log10)"];
			data_summary["Error (log10)"] = parsedFinalSampleLine["Error (log10)"];
			data_summary["Absolute Error (log10)"] = parsedFinalSampleLine["Absolute Error (log10)"];
			data_summary["Reference Z Value (log10)"] = parsedFinalSampleLine["Reference Z Value (log10)"];
			data_summary["Estimated Error (log10)"] = parsedFinalSampleLine["Estimated Error (log10)"];
			data_summary["Estimated Absolute Error (log10)"] = parsedFinalSampleLine["Estimated Absolute Error (log10)"];

			data_summary["Z Estimate (ln)"] = parsedFinalSampleLine["Z Estimate (ln)"];
			data_summary["Exact Z Value (ln)"] = parsedFinalSampleLine["Exact Z Value (ln)"];
			data_summary["Error (ln)"] = parsedFinalSampleLine["Error (ln)"];
			data_summary["Absolute Error (ln)"] = parsedFinalSampleLine["Absolute Error (ln)"];
			data_summary["Reference Z Value (ln)"] = parsedFinalSampleLine["Reference Z Value (ln)"];
			data_summary["Estimated Error (ln)"] = parsedFinalSampleLine["Estimated Error (ln)"];
			data_summary["Estimated Absolute Error (ln)"] = parsedFinalSampleLine["Estimated Absolute Error (ln)"];

			data_summary["Average Number of Nodes Created Per Probe"] = parsedFinalSampleLine["Average Number of Nodes Created Per Probe"];

			data_summary["Time"] = parsedFinalSampleLine["Time"];


	# extract information from stderr
	if stderr_file_Path != None:
		data_summary["stderr file path"] = str(stderr_file_Path.relative_to(root));
		with stderr_file_Path.open('r') as stderr_file:
			for i, line in enumerate(stderr_file):
				data_summary["error line " + str(i)] = line.strip();

	return data_summary, parsedSampleLines;

def summarizeProbeLogs(experiment_files_by_type_Dict, options=None, root=Path("")):
	options = formatOptions(options)
	if "stdout" not in experiment_files_by_type_Dict:
		return None;
	data_summary = OrderedDict()
	output_file_Path = experiment_files_by_type_Dict["stdout"];
	data_summary["stdout file path"] = str(output_file_Path.relative_to(root));


	# extract probe log information from stdout
	with output_file_Path.open('r') as fin:

		# read in header
		readLines = readLinesUntil(fin, _startswith="", _strip=True)
		if readLines[NUM_LINES_READ_IN] != 0:
			problem = Path(readLines[CURR_LINE].split()[1]).stem

			nProbesReadIn = 0
			nLevelsProcessed = 0
			totalNumAbstractStates = 0
			sumSingletonRatios = 0
			sumVariancesBetweenSizeOfAbstractStates = 0
			
			numAbstractStates = 0
			numSigletons = None
			abstractStateSizes = None

			while readLines[MATCH_FOUND]==True:
				readLines = readLinesUntil(fin, _startswith=["Probe:", "Var:", "Abstract State:"], _strip=True)
				if readLines[MATCH_FOUND]==False:
					break;

				# New probe case
				if readLines[MATCH_IDX]==0:
					nProbesReadIn += 1
					probeNum = int(readLines[CURR_LINE].split()[1])
					assert(probeNum == nProbesReadIn)

				# New var
				elif readLines[MATCH_IDX]==1:
					# compile results from old var
					if numAbstractStates != 0:
						assert(numAbstractStates == len(abstractStateSizes))
						totalNumAbstractStates += numAbstractStates
						sumSingletonRatios += numSigletons/numAbstractStates
						sumVariancesBetweenSizeOfAbstractStates += np.var(abstractStateSizes)
						nLevelsProcessed += 1
					# reset counters
					numAbstractStates = 0
					numSigletons = 0
					abstractStateSizes = []

				# Abstract state case
				elif readLines[MATCH_IDX]==2:
					# count number of nodes
					readLines = readLinesUntil(fin, _startswith="Selected Representative:", _strip=True)
					numNodes = readLines[NUM_LINES_READ_IN] - 1
					assert(numNodes >= 1)
					numAbstractStates += 1
					if numNodes == 1:
						numSigletons += 1
					abstractStateSizes.append(numNodes)

			data_summary["ave num abstract states"] = totalNumAbstractStates / nLevelsProcessed
			data_summary["ave singleton ratio"] = sumSingletonRatios / nLevelsProcessed
			data_summary["ave variance between size of abstract states"] = sumVariancesBetweenSizeOfAbstractStates / nLevelsProcessed

	return data_summary