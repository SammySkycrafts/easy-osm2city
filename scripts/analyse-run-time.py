#! /usr/bin/python
import sys
from tabulate import tabulate
import re
import os
import json

sortkey = []
ifile = ""
cache = True

argc = len(sys.argv)
first = 1
i = 1
while i < argc:
	if sys.argv[i] == "-s" or sys.argv[i] == "--sort-by":
		i += 1
		if len(sortkey) <= 3:
			if sys.argv[i] in ["max", "occ", "avg", "sum"]:
				sortkey.append(sys.argv[i])
			else:
				print("ERROR: Unknown key " + sys.argv[i] + ": Aborting!")
				sys.exit(1)
		else:
			print("WARNING: Too many sort criteria given! Will ignore last argument.")
	elif sys.argv[i] == "-n" or sys.argv[i] == "--no-cache":
		cache = False
	elif sys.argv[i] == "-h" or sys.argv[i] == "--help":
		print("usage: analyse-run-time.py <log-path> [OPTIONS]")
		print("Showing, how long certain tasks took")
		print("")
		print("OPTIONS")
		print("  -s, --sort-by  Sort by key. Can be specified up to 3 times.")
		print("                 First key has highest priority")
		print("                 Valid keys are:")
		print("                   max (default) Maximum execution time")
		print("                   avg Average execution time")
		print("                   sum Total execution time")
		print("                   occ Occurrences in the log file")
		print("  -n, --no-cache Doesn't read and write from/to cache file")
		print("  -h, --help     Shows this help and exit")
		sys.exit(0)
	else:
		if first == 1:
			first = 0
			ifile = sys.argv[i]
		else:
			print("Unknown option " + sys.argv[i])
			sys.exit(1)
	i += 1

if len(sortkey) == 0:
	sortkey.append("max")

from_cache = False
if os.path.isfile(ifile + ".cache") and cache:
	read_src = False
	from_cache = True
	with open(ifile + ".cache") as json_data:
		tasks = json.load(json_data)
else:
	read_src = True

if read_src:
	times = []
	try:
		with open(ifile) as f:
			for line in f:
				match = re.findall("SpawnPoolWorker-\d+ root INFO +Time used in seconds for (.*): (\d+\.\d+)", line)
				if match != []:
					times.append(match[0])
                                match = re.findall("SpawnPoolWorker-\d+ root INFO +(Reading OSM .* data for \['.*'\]) from db took (\d+\.\d+) seconds.", line)
                                if match != []:
                                        times.append(match[0])
	except:
		print("err")
		sys.exit(1)

	tasks = []
	for time in times:
		found = False
		for i in range(0, len(tasks)):
			if tasks[i]['name'] == time[0]:
				tasks[i]['occ'] += 1
				tasks[i]['sum'] += float(time[1])
				if float(time[1]) > tasks[i]['max']:
					tasks[i]['max'] = float(time[1])
				found = True
				break
		if not found:
			tasks.append({})
			tasks[len(tasks) -1]['name'] = time[0]
			tasks[len(tasks) -1]['occ'] = 1
			tasks[len(tasks) -1]['sum'] = float(time[1])
			tasks[len(tasks) -1]['max'] = float(time[1])

	for task in tasks:
		task['avg'] = task['sum'] / task['occ']

	if cache:
		with open(ifile + ".cache", "w") as f:
			f.write(json.dumps(tasks, default=lambda o: o.__dict__))

if from_cache:
	print("Data from cache used")

i = len(sortkey) - 1
while i >= 0:
	tasks.sort(key=lambda tasks: tasks[sortkey[i]], reverse=True)
	i -= 1
print tabulate(tasks,headers="keys",floatfmt=".2f")
