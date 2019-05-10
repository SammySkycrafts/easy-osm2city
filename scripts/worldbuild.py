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
						elif n == -80:
							world = 2
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
							tile = ((10 - wm) % 10) * 10 + cs * cs * (nm / cs)

							
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
		print("  -s, --chunk-size  Sets chunk size,  default 5")
		print("  -t, --threads     Number of threads to run")
		print("  -c, --continue    Contine build from tile number <n>")
		print("  -h, --help        Shows this help and exit")
		print("  -p, --progress    Shows progress and exit")
		sys.exit(0)
	else:
		if first == 1:
			first = 0
			pbf_path = sys.argv[i]
		else:
			print("Unknown option " + sys.argv[i])
			sys.exit(1)
	i += 1

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
		run("zip -rq projects/worldbuild/output/error/" + name + ".zip projects/worldbuild/scenery/ ")

		# Trigger failed after build script
		if os.path.isfile("./scripts/afterbuild-failed"):
			os.system("./scripts/afterbuild-failed " + name + " &")
	else:
		run("zip -rq projects/worldbuild/output/" + name + ".zip projects/worldbuild/scenery/ ")

		# Trigger after build script
		if os.path.isfile("./scripts/afterbuild-success"):
			os.system("./scripts/afterbuild-success " + name + " &")

def prepare():
	run("./delete-db worldbuild")
	run("./create-db worldbuild")

	run("rm -rf projects/worldbuild/scenery/*")
	run("./clear-cache-files worldbuild")

def run_all(name, w, s, e, n, chunk_size, threads, cont=False):
	global pbf_path
	if os.system("ls -l " + pbf_path + name + ".osm.pbf | grep ' 73 ' > /dev/null") != 0:
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
if os.path.isfile("projects/worldbuild/exclude"):
	with open("projects/worldbuild/exclude") as json_data:
		exclude = json.load(json_data)
else:
	exclude = []

start_time = time.time()

# Build poles first
if not "n-pole" in exclude:
	run_all("n-pole", -180, 80, 180, 90, 360, threads)

if not "s-pole" in exclude:
	run_all("s-pole", -180, -90, 180, -80, 360, threads)

if cont != 0:
	tile = cont - 2
	tile_in_row = ((tile - 1) % 36) - 18
	ii = (tile - tile_in_row - 19) / 36 - 8
else:
	ii = -8
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

print_build_time(start_time, time.time())


