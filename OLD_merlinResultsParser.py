import math

from pathlib import Path
from collections import OrderedDict


def readlines_until(file, prefix="", contains=""):
	final_line = None;
	for line in file:
		# print(line)
		# print(line[0])
		if line.startswith(prefix) and contains in line:
			final_line = line;
			break;
	return final_line;


def get_search_line_tokens(line):
	search_line_tokens = None;
	line_split_by_time = line[1:].split("]");
	time = line_split_by_time[0];
	time = time.replace("*","").strip();
	line_excluding_time = line_split_by_time[1].replace('(',"").replace(')',"");
	search_line_tokens = [time] + line_excluding_time.split();
	return search_line_tokens;

def parse_any_ldfs_bounded_search_line(line):
	search_line_data = OrderedDict()
	search_line_tokens = get_search_line_tokens(line);
	search_line_data["time"] = search_line_tokens[0]
	search_line_data["log lower bound"] = search_line_tokens[6];
	search_line_data["log upper bound"] = search_line_tokens[8];
	return search_line_data;

def parse_any_rbfaoo_ublb_search_line(line):
	search_line_data = OrderedDict()
	search_line_tokens = get_search_line_tokens(line);
	search_line_data["time"] = search_line_tokens[0]
	search_line_data["log lower bound"] = search_line_tokens[7];
	search_line_data["log upper bound"] = search_line_tokens[9];
	return search_line_data;

def parse_any_sbfs_bounded_search_line(line):
	search_line_data = OrderedDict()
	search_line_tokens = get_search_line_tokens(line);
	search_line_data["time"] = search_line_tokens[0]
	search_line_data["log lower bound"] = search_line_tokens[6];
	search_line_data["log upper bound"] = search_line_tokens[8];
	return search_line_data;

def parse_aobb_search_line(line):
	search_line_data = OrderedDict()
	search_line_tokens = get_search_line_tokens(line);
	search_line_data["time"] = search_line_tokens[0]
	search_line_data["log lower bound"] = search_line_tokens[8];
	return search_line_data;

def parse_kstar_aobb_search_line(line):
	search_line_data = OrderedDict()
	search_line_tokens = get_search_line_tokens(line);
	search_line_data["time"] = search_line_tokens[0]
	search_line_data["log lower bound"] = search_line_tokens[8];
	return search_line_data;

def parse_braobb_search_line(line):
	search_line_data = OrderedDict()
	search_line_tokens = get_search_line_tokens(line);
	search_line_data["time"] = search_line_tokens[0]
	search_line_data["log lower bound"] = search_line_tokens[8];
	return search_line_data;

def parse_rbfaoo_search_line(line):
	search_line_data = OrderedDict()
	search_line_tokens = get_search_line_tokens(line);
	search_line_data["time"] = search_line_tokens[0]
	search_line_data["log lower bound"] = search_line_tokens[5];
	return search_line_data;

ALGORITHM_TO_SEARCH_LINE_PARSER_Dict = { "any-ldfs-bounded"		:		parse_any_ldfs_bounded_search_line,
										 "any-rbfaoo-ublb"		:		parse_any_rbfaoo_ublb_search_line,
										 "any-sbfs-bounded"		:		parse_any_sbfs_bounded_search_line,
										 "aobb"					:		parse_aobb_search_line,
										 "braobb"				:		parse_braobb_search_line,
										 "rbfaoo"				:		parse_rbfaoo_search_line,
										 "kstar-aobb"			:		parse_kstar_aobb_search_line,
										 }



def summarizeData(experiment_files_by_type_Dict, root=Path("")):
	data_summary = OrderedDict()
	stdout_file_Path = experiment_files_by_type_Dict["stdout"];
	stderr_file_Path = experiment_files_by_type_Dict["stderr"];

	# extract information from stdout
	data_summary["stdout file path"] = str(stdout_file_Path.relative_to(root));
	with stdout_file_Path.open('r') as stdout_file:
		for i in range(1):
			# skip program information
			line = readlines_until(stdout_file, "------------------------------------------------------------------");
			line = readlines_until(stdout_file, "------------------------------------------------------------------");
		
			# Command line input
			line = readlines_until(stdout_file, "");
			if line==None:
				break;
			data_summary["Command line input"] = line.strip();

			# ###
			line = readlines_until(stdout_file, "+ i-bound:");
			if line==None:
				break;
			line_tokens = line.split(":");
			iB = line_tokens[1].strip();
			data_summary["iB"] = iB;

			while(line.startswith("+")):
				# print(line)
				line = readlines_until(stdout_file, "");
				assert(line != None)
				if line.startswith("+"):
					line_tokens = line.split(":");
					key = line_tokens[0].split('+')[1].strip()
					value = line_tokens[1].strip();
					data_summary[key] = value;
					if key == "Algorithm":
						algorithm = value

			# # ###
			# line = readlines_until(stdout_file, "+ Algorithm:");
			# if line==None:
			# 	break;
			# line_tokens = line.split(":");
			# algorithm = line_tokens[1].strip();
			# data_summary["Algorithm"] = algorithm;

			# Determinism ratio
			line = readlines_until(stdout_file, "Determinism ratio:");
			if line==None:
				break;
			line_tokens = line.split(":");
			determinism_ratio = line_tokens[1].strip();
			data_summary["Determinism ratio"] = determinism_ratio;

			# Created problem before evidence
			line = readlines_until(stdout_file, "Created problem with");
			if line==None:
				break;
			line_tokens = line.split("with");
			variables_and_functions_without_evidence = line_tokens[1].strip()[:-1]; # [:-1] slices string to remove last character which is a period
			data_summary["Created problem before evidence"] = variables_and_functions_without_evidence;

			# Created problem after evidence
			line = readlines_until(stdout_file, "Removed evidence, now");
			if line==None:
				break;
			line_tokens = line.split("now");
			variables_and_functions_with_evidence = line_tokens[1].strip()[:-1]; # [:-1] slices string to remove last character which is a period
			data_summary["Created problem after evidence"] = variables_and_functions_with_evidence;

			# Max. domain size
			line = readlines_until(stdout_file, "Max. domain size:");
			if line==None:
				break;
			line_tokens = line.split(":");
			max_domain_size = line_tokens[1].strip();
			data_summary["Max. domain size"] = max_domain_size;

			# Max. function arity
			line = readlines_until(stdout_file, "Max. function arity:");
			if line==None:
				break;
			line_tokens = line.split(":");
			max_fxn_arity = line_tokens[1].strip();
			data_summary["Max. function arity"] = max_fxn_arity;

			# Graph
			line = readlines_until(stdout_file, "Graph with");
			if line==None:
				break;
			line_tokens = line.split("with");
			nodes_and_edges = line_tokens[1].strip()[:-1]; # [:-1] slices string to remove last character which is a period
			data_summary["Graph"] = nodes_and_edges;

			# MAP variables
			line = readlines_until(stdout_file, "MAP:");
			if line==None:
				break;
			line_tokens = line.split(":");
			MAP_variables = line_tokens[1].strip();
			data_summary["MAP variables"] = MAP_variables;

			# Induced width
			line = readlines_until(stdout_file, "Induced width:");
			if line==None:
				break;
			line_tokens = line.split(":");
			induced_width = line_tokens[1].strip();
			data_summary["Induced width"] = induced_width;

			# Pseudotree depth
			line = readlines_until(stdout_file, "Pseudotree depth:");
			if line==None:
				break;
			line_tokens = line.split(":");
			pseudotree_depth = line_tokens[1].strip();
			data_summary["Pseudotree depth"] = pseudotree_depth;

			# Problem variables
			line = readlines_until(stdout_file, "Problem variables:");
			if line==None:
				break;
			line_tokens = line.split(":");
			problem_variables = line_tokens[1].strip();
			data_summary["Problem variables"] = problem_variables;

			# MAP log bound
			line = readlines_until(stdout_file, "MAP log Bound");
			if line==None:
				break;
			line_tokens = line.split("Bound");
			MAP_log_bound = line_tokens[1].strip();
			data_summary["MAP log bound"] = MAP_log_bound;

			# Log bound
			line = readlines_until(stdout_file, "Log Bound:");
			if line==None:
				break;
			line_tokens = line.split(":");
			log_bound = line_tokens[1].strip();
			data_summary["Log bound"] = log_bound;

			# Check if search ensued
			line = readlines_until(stdout_file, "Initialization complete:");
			line = stdout_file.readline().strip()
			if not "Solved during initialization" in line: # progress to Search results

				# Search results
				if "Starting search" not in line:
					line = readlines_until(stdout_file, "--- Starting search ---");
				readlines_until(stdout_file, "m_subunitStabilityThresholds:");
				line = readlines_until(stdout_file, "");
				if line==None:
					break;
				if line.startswith('['):
					for j in range(1):
						# extract search data
						search_line_parser = ALGORITHM_TO_SEARCH_LINE_PARSER_Dict[algorithm];
						# first search line
						search_line_data = search_line_parser(line);
						for key,value in search_line_data.items():
							data_summary["Search start " + key] = value;
						# last search line
						prev_line = line;
						curr_line = readlines_until(stdout_file, "");
						next_line = readlines_until(stdout_file, "");
						if curr_line==None:
							for key,value in search_line_data.items():
								data_summary["Search end " + key] = value;
							break;
						elif not curr_line.strip():
							for key,value in search_line_data.items():
								data_summary["Search end " + key] = value;
							break;
						else:
							while next_line is not None and next_line.strip():
								prev_line = curr_line;
								curr_line = next_line;
								next_line = readlines_until(stdout_file, "");
							last_search_line = None;
							if curr_line.startswith('['):
								last_search_line = curr_line;
							else:
								last_search_line = prev_line;
							search_line_data = search_line_parser(last_search_line);
							for key,value in search_line_data.items():
								data_summary["Search end " + key] = value;

				# Advance to summary section
				line = readlines_until(stdout_file, prefix="---", contains="Search done");

			# Status
			line = readlines_until(stdout_file, "Status:");
			if line==None:
					break;
			line_tokens = line.split(":");
			status = line_tokens[1].strip();
			data_summary["Status"] = status;

			if status == "success":
				# OR nodes
				line = readlines_until(stdout_file, "OR nodes:");
				assert(line), data_summary["Command line input"]
				line_tokens = line.split(":");
				solution = line_tokens[1].split()[0].strip();
				data_summary["OR nodes"] = solution;

				# AND nodes
				line = readlines_until(stdout_file, "AND nodes:");
				assert(line), data_summary["Command line input"]
				line_tokens = line.split(":");
				solution = line_tokens[1].split()[0].strip();
				data_summary["AND nodes"] = solution;

				# OR nodes (MAP)
				line = readlines_until(stdout_file, "OR nodes (MAP):");
				assert(line), data_summary["Command line input"]
				line_tokens = line.split(":");
				solution = line_tokens[1].split()[0].strip();
				data_summary["OR nodes (MAP)"] = solution;

				# AND nodes (MAP)
				line = readlines_until(stdout_file, "AND nodes (MAP):");
				assert(line), data_summary["Command line input"]
				line_tokens = line.split(":");
				solution = line_tokens[1].split()[0].strip();
				data_summary["AND nodes (MAP)"] = solution;

				# Deadends (CP)
				line = readlines_until(stdout_file, "Deadends (CP):");
				assert(line), data_summary["Command line input"]
				line_tokens = line.split(":");
				solution = line_tokens[1].split()[0].strip();
				data_summary["Deadends (CP)"] = solution;

				# Deadends (UB)
				line = readlines_until(stdout_file, "Deadends (UB):");
				assert(line), data_summary["Command line input"]
				line_tokens = line.split(":");
				solution = line_tokens[1].split()[0].strip();
				data_summary["Deadends (UB)"] = solution;

				if(algorithm == "kstar-aobb"):
					# Deadends (SSP)
					line = readlines_until(stdout_file, "Deadends (SSP):");
					assert(line), data_summary["Command line input"]
					line_tokens = line.split(":");
					solution = line_tokens[1].split()[0].strip();
					data_summary["Deadends (SSP)"] = solution;

					# Exact Heuristic
					line = readlines_until(stdout_file, "Exact Heuristic:");
					assert(line), data_summary["Command line input"]
					line_tokens = line.split(":");
					solution = line_tokens[1].split()[0].strip();
					data_summary["Exact Heuristic"] = solution;

					# Dynamic Heuristic
					prevLine = line;
					line = readlines_until(stdout_file, "Dynamic Hueristic:");
					assert(line), data_summary["Command line input"] + "\n\n" + prevLine + "\n\n" + "Check 'Heuristic' spelling in code and in output file" + "\n\n" 
					line_tokens = line.split(":");
					solution = line_tokens[1].split()[0].strip();
					data_summary["Dynamic Heuristic"] = solution;

				# Time elapsed
				line = readlines_until(stdout_file, "Time elapsed:");
				assert(line), data_summary["Command line input"]
				line_tokens = line.split(":");
				solution = line_tokens[1].split()[0].strip();
				data_summary["Time elapsed"] = solution;

				# Preprocessing time
				line = readlines_until(stdout_file, "Preprocessing:");
				assert(line), data_summary["Command line input"]
				line_tokens = line.split(":");
				solution = line_tokens[1].split()[0].strip();
				data_summary["Preprocessing time"] = solution;

				# Solution
				line = readlines_until(stdout_file, "Solution:");
				assert(line), data_summary["Command line input"]
				line_tokens = line.split(":");
				full_solution_printout = line_tokens[1].strip();
				full_solution_printout_tokens = full_solution_printout.split();
				solution = full_solution_printout_tokens[0].strip();
				data_summary["Solution"] = solution;
				ln_solution = full_solution_printout_tokens[1].replace('(','').replace(')','').strip();
				data_summary["Solution (ln)"] = ln_solution;
				# try:
				data_summary["Solution (log10)"] = str(float(ln_solution)/math.log(10));
				# except:
				# 	print("full_solution_printout", full_solution_printout)
				# 	print("full_solution_printout_tokens")
				# 	for t in full_solution_printout_tokens:
				# 		print("\t", t)
				# 	print("solution", solution)
				# 	print("ln_solution", ln_solution)
				# 	exit()

	# extract information from stderr
	data_summary["stderr file path"] = str(stderr_file_Path.relative_to(root));
	with stderr_file_Path.open('r') as stderr_file:
		for i, line in enumerate(stderr_file):
			data_summary["error line " + str(i)] = line.strip();

	return data_summary;