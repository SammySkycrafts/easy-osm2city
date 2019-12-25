#! /usr/bin/python
# Copyright (C) 2018-2019 Merspieler, merspieler _at_ airmail.cc
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
import sys
import math
import re
import json
import time

chunk_size = 5
threads = 5
cont = 0
exclude = []
pbf_path = ""
db_strategy = "demand"
db_prefix = ""
skip_started = False

argc = len(sys.argv)
i = 1
first = 1
while i < argc:
	if sys.argv[i] == "-s" or sys.argv[i] == "--chunk-size":
		i += 1
		chunk_size = sys.argv[i]
	elif sys.argv[i] == "-c" or sys.argv[i] == "--continue":
		i += 1
		cont = int(sys.argv[i])
	elif sys.argv[i] == "-t" or sys.argv[i] == "--threads":
		i += 1
		threads = sys.argv[i]
	elif sys.argv[i] == "-e" or sys.argv[i] == "--exclude":
		i += 1
		if os.path.isfile(sys.argv[i]):
			try:
				with open(sys.argv[i]) as json_data:
					exclude += json.load(json_data)
			except ValueError:
				print("Exclude file '" + sys.argv[i] + "' is no proper JSON file.")
				sys.exit(1)
		else:
			print("File not found: " + sys.argv[i])
			sys.exit(1)
	elif sys.argv[i] == "-D" or sys.argv[i] == "--database-startegy":
		i += 1
		if sys.argv[i] == "mono" or sys.argv[i] == "demand" or sys.argv[i] == "chunk":
			db_strategy = sys.argv[i]
		else:
			print("ERROR: Unknown database startegy " + sys.argv[i])
			sys.exit(1)
	elif sys.argv[i] == "-P" or sys.argv[i] == "--database-prefix":
		i += 1
		db_prefix = sys.argv[i]
	elif sys.argv[i] == "--skip-started":
		skip_started = True
	elif sys.argv[i] == "-p" or sys.argv[i] == "--progress":
		try:
			with open("projects/worldbuild/done") as f:
				lines = f.readlines()
				for line in lines:
					match = re.findall("(-?[0-9]{1,3}\.?[0-9]{0,4})_(-?[0-9]{1,3}\.?[0-9]{0,4})_(-?[0-9]{1,3}\.?[0-9]{0,4})_(-?[0-9]{1,3}\.?[0-9]{0,4})", line)
					if match != []:

						w = float(match[0][0])
						s = float(match[0][1])
						e = float(match[0][2])
						n = float(match[0][3])

						if n == 90:
							world = 1
							tile = "N/A"
						elif n == -80:
							world = 2
							tile = "N/A"
						else:
							wm = w % 10
							sm = s % 10
							em = e % 10
							nm = n % 10

							wM = (int(w) - wm) / 10
							sM = (int(s) - sm) / 10
							eM = (int(e) - em) / 10
							nM = (int(n) - nm) / 10

							cs = n - s
							if nm == 0:
								nm = 10
							tile = (wm % 10) * 10 + cs * cs * (nm / cs)

							
							rows = 0
							while sM > -8:
								rows += 1
								sM -= 1

							world = 3 + 36 * rows + wM + 18

						print("Current worldbuild tile is " + str(int(world)) + "/578")
						print("Current tile " + str(tile) + "% complete")
						sys.exit(0)
					else:
						print("Unable to get progress")
						sys.exit(1)
		except IOError:
			print("Unable to get progress")
			sys.exit(1)
	elif sys.argv[i] == "-h" or sys.argv[i] == "--help":
		print("usage: worldbuild <pbf-path> [OPTIONS]")
		print("Builds the world")
		print("")
		print("OPTIONS")
		print("  -s, --chunk-size         Sets chunk size,  default 5")
		print("  -t, --threads            Number of threads to run")
		print("  -c, --continue           Contine build from tile number <n> when building with 'demand' strategy")
		print("  -e, --exclude            Files containing JSON array naming tiles not to be build")
		print("                           Can be used multiple times.")
		print("                           If not given projects/worldbuild/exclude will be used")
		print("  -D, --database-strategy  Database strategies:")
		print("                           - demand: Uses database 'worldbuild' and imports tiles on demand")
                print("                             clears db before next tile. Default behaviour")
		print("                           - chunk: Expects one database per chunk")
		print("                           - mono: Expexcting database 'worldbuild' containing world wide data")
		print("                             NOT YET IMPLEMENTED")
		print("  -P, --database-prefix    When db startegy is chunk, prefix tile names with <prefix>")
		print("      --skip-started       Skip tiles flaged as started when running with 'chunk' or 'mono' strategy")
		print("  -h, --help               Shows this help and exit")
		print("  -p, --progress           Shows progress and exit")
		sys.exit(0)
	else:
		if first == 1:
			first = 0
			pbf_path = sys.argv[i]
		else:
			print("Unknown option " + sys.argv[i])
			sys.exit(1)
	i += 1

if pbf_path == "" and db_strategy == "demand":
	print("No pbf-path was given, exiting...")
	sys.exit(1)

def run(command):
	exit_code = os.system(command)
	if exit_code == 0:
		return
	elif exit_code == 130:
		print("Aborted!")
		sys.exit(130)
	else:
		print("Sub process '" + command + "'exited with code " + str(exit_code) + ". Aborting!")
		sys.exit(4)

run("mkdir -p projects/worldbuild/output/error")

def build_tile(name, west, south, east, north, chunk_size, threads, cont=False):
	global pbf_path
	if west < 0:
		west = "*" + str(west)
	else:
		west = str(west)
	south = str(south)
	east = str(east)
	north = str(north)

	run("./read-pbf worldbuild " + pbf_path + name + ".osm.pbf")
	run('echo "bounds=' + west + "_" + south + "_" + east + "_" + north + '" > projects/worldbuild/settings')
	run("./build worldbuild --chunk-size " + str(chunk_size) + " -t " + str(threads))

def after_build(name):
	if os.path.isfile("projects/worldbuild/osm2city-exceptions.log"):
		run("mv projects/worldbuild/osm2city-exceptions.log projects/worldbuild/output/error/" + name + ".exceptions.log")
		# Trigger failed after build script
		if os.path.isfile("./scripts/afterbuild-failed"):
			os.system("bash -c './scripts/afterbuild-failed " + name + " &'")
	else:
		# Trigger after build script
		if os.path.isfile("./scripts/afterbuild-success"):
			os.system("bash -c './scripts/afterbuild-success " + name + " &'")

def prepare():
	run("./delete-db worldbuild")
	run("./create-db worldbuild")

	run("./clear-cache-files worldbuild")

def run_all(name, w, s, e, n, chunk_size, threads, cont=False):
	global pbf_path
	if os.system("ls -l " + pbf_path + name + ".osm.pbf | grep ' 73 ' > /dev/null") != 0:
		if cont == False:
			prepare()
		build_tile(name, w, s, e, n, chunk_size, threads, cont)
		after_build(name)
	else:
		print("INFO: Skipping " + name + " because pbf file is empty")

def norm(num, length):
	num = str(num)
	while len(num) < length:
		num = "0" + num
	return num

def print_build_time(start_time, end_time):
	elapsed = end_time - start_time
	seconds = elapsed % 60
	elapsed = (elapsed - seconds) / 60
	minutes = elapsed % 60
	elapsed = (elapsed - minutes) / 60
	hours = elapsed % 24
	days = (elapsed - hours) / 24

	time = str(int(hours)) + " Hours, " + str(int(minutes)) + " Minutes and " + str(int(seconds)) + " Seconds"
	if days > 0:
        	time = str(int(days)) + " Days, " + time

	print("Running worldbuild took " + time)

# Get exclude file
if os.path.isfile("projects/worldbuild/exclude") and exclude == []:
	try:
		with open("projects/worldbuild/exclude") as json_data:
			exclude = json.load(json_data)
	except ValueError:
		print("Exclude file 'projects/worldbuild/exclude' is no proper JSON file.")
		sys.exit(1)

start_time = time.time()

if db_strategy == "demand":
	if cont != 0:
		tile = cont - 2
		tile_in_row = ((tile - 1) % 36) - 18
		ii = (tile - tile_in_row - 19) / 36 - 8
	else:
		ii = -8
	# Build poles first
	if not "n-pole" in exclude and cont <= 1:
		run_all("n-pole", -180, 80, 180, 90, 360, threads)
	
	if not "s-pole" in exclude and cont <= 2:
		run_all("s-pole", -180, -90, 180, -80, 360, threads)
	
	while ii < 8:
		i = ii * 10
		if cont != 0:
			jj = tile_in_row
		else:
			jj = -18
		while jj < 18:
			j = jj * 10
			if i >= 0:
				ns = "n"
			else:
				ns = "s"
			if j >= 0:
				ew = "e"
			else:
				ew = "w"
	
			name = ew + norm(abs(j), 3) + ns + norm(abs(i), 2)
	
			if not name in exclude:
				if cont != 0:
					run_all(name, j, i, j + 10, i + 10, chunk_size, threads, cont=True)
					cont = 0
				else:
					run_all(name, j, i, j + 10, i + 10, chunk_size, threads, cont=False)
			jj += 1
		ii += 1
elif db_strategy == "chunk":
	if os.path.isfile("projects/worldbuild/status"):
		try:
			with open("projects/worldbuild/status") as json_data:
				status = json.load(json_data)
		except ValueError:
			print("ERROR: Invalid status file")
			sys.exit(1)
	else:
		status = {}

	tile_list = ""

	# Build poles first
	if not "n-pole" in exclude and (not "n-pole" in status or ("n-pole" in status and status["n-pole"]["status"] != "done")):
		tile_list += "n-pole\n"
	if not "s-pole" in exclude and (not "s-pole" in status or ("s-pole" in status and status["s-pole"]["status"] != "done")):
		tile_list += "s-pole\n"

	ii = -8
	
	while ii < 8:
		i = ii * 10
		jj = -18
		while jj < 18:
			j = jj * 10
			if i >= 0:
				ns = "n"
			else:
				ns = "s"
			if j >= 0:
				ew = "e"
			else:
				ew = "w"
	
			name = ew + norm(abs(j), 3) + ns + norm(abs(i), 2)
	
			if not name in exclude and (not name in status or (name in status and status[name]["status"] != "done")):
				if ns == "s":
					ns_step = -1
				else:
					ns_step = 1
				if ew == "w":
					ew_step = -1
				else:
					ew_step = 1
				j = abs(j)
				for k in range(0, 10):
					iii = abs(i)
					for l in range(0, 10):
						name_minor = ew + norm(j, 3) + ns + norm(iii, 2)
						if not name_minor in exclude and (not name in status or (not name_minor in status[name] or (name_minor in status[name] and (status[name][name_minor]["status"] != "done" and (status[name][name_minor]["status"] == "started" and not skip_started))))):
							tile_list = tile_list + name_minor + "\n"
						iii += ns_step
					j += ew_step
			jj += 1
		ii += 1

	db_prefix = "-p " + db_prefix
	os.system("echo '" + tile_list + "' | parallel --eta -j " + str(threads) + " ./scripts/build-chunk.py {} " + str(db_prefix))
elif db_startegy == "mono":
	print("ERROR: NOT YET IMPLEMENTED")
	sys.exit(1)

print_build_time(start_time, time.time())


