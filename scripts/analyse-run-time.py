#! /usr/bin/python
import sys
from tabulate import tabulate
import re

sortkey = "max"
ifile = ""

argc = len(sys.argv)
first = 1
i = 1
while i < argc:
	if sys.argv[i] == "-s" or sys.argv[i] == "--sort-by":
		i += 1
		sortkey = sys.argv[i]
	elif sys.argv[i] == "-h" or sys.argv[i] == "--help":
		print("usage: analyse-run-time.py <log-path> [OPTIONS]")
		print("Showing, how long certain tasks took")
		print("")
		print("OPTIONS")
		print("  -s, --sort-by  Sort by key:")
		print("                 Valid keys are:")
		print("                   max (default) Maximum execution time")
		print("                   avg Average execution time")
		print("                   sum Total execution time")
		print("                   occ Occurrences in the log file")
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

times = []
try:
	with open(ifile) as f:
		lines = f.readlines()
		for line in lines:
			match = re.findall("SpawnPoolWorker-\d+ root INFO +Time used in seconds for (.*): (\d+\.\d+)", line)
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

#sorted(tasks, key=attrgetter('max'))
tasks.sort(key=lambda tasks: tasks[sortkey], reverse=True)

print tabulate(tasks,headers="keys",floatfmt=".2f")
