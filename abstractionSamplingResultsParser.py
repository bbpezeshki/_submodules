from pathlib import Path
from collections import OrderedDict
import math


def readlines_until(file, prefix=""):
	final_line = None;
	for line in file:
		if line.startswith(prefix):
			final_line = line;
			break;
	return final_line;

def readlines_untile_last_non_empty_line(file):
	final_line = None;
	for line in file:
		line = line.strip();
		if line:
			final_line = line;
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
	number_of_nodes_in_final_sampling_tree = final_sample_line_tokens[7];
	return number_of_nodes_in_final_sampling_tree;



def summarizeData(experiment_files_by_type_Dict, root=Path("")):
	data_summary = OrderedDict()
	output_file_Path = experiment_files_by_type_Dict["output"];
	stderr_file_Path = experiment_files_by_type_Dict["stderr"];

	# extract information from stdout
	data_summary["output file path"] = str(output_file_Path.relative_to(root));
	with output_file_Path.open('r') as output_file:
		for i in range(1):

			# Get First Line (Program Parameters) Tokens
			line = readlines_until(output_file, "");
			if line==None:
				break;
			program_parameters_line_tokens = strip_and_split(line);

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


			# Read until final non-empty line
			final_sample_line = readlines_untile_last_non_empty_line(output_file);
			if final_sample_line==None:
				break;
			final_sample_line_tokens = strip_and_split(final_sample_line);

			# Number of Samples
			number_of_samples = get_number_of_samples_from_final_sample_line_tokens(final_sample_line_tokens);
			data_summary["Number of Samples"] = number_of_samples;

			# Final Z Estimate
			final_Z_estimate_log10 = get_final_Z_estimate_from_final_sample_line_tokens(final_sample_line_tokens);
			data_summary["Final Z Estimate (log10)"] = final_Z_estimate_log10;
			final_Z_estimate_ln = float(final_Z_estimate_log10)/math.log(math.exp(1),10);
			data_summary["Final Z Estimate (ln)"] = str(final_Z_estimate_ln);
			

			# Number of Nodes in Final Sampling Tree
			number_of_nodes_in_final_sampling_tree = get_number_of_nodes_in_final_sampling_tree_from_final_sample_line_tokens(final_sample_line_tokens);
			data_summary["Number of Nodes in Final Sampling Tree"] = number_of_nodes_in_final_sampling_tree;



	# extract information from stderr
	data_summary["stderr file path"] = str(stderr_file_Path.relative_to(root));
	with stderr_file_Path.open('r') as stderr_file:
		for i, line in enumerate(stderr_file):
			data_summary["error line " + str(i)] = line.strip();

	return data_summary;