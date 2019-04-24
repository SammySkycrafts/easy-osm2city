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

argc = len(sys.argv)
i = 1
first = 1
while i < argc:
	if sys.argv[i] == "-p" or sys.argv[i] == "--progress":
		try:
			with open("projects/worldbuild/done") as f:
				lines = f.readlines()
				for line in lines:
					match = re.findall("(-?[0-9]{1,3}\.?[0-9]{0,4})_-?[0-9]{1,3}\.?[0-9]{0,4}_-?[0-9]{1,3}\.?[0-9]{0,4}_(-?[0-9]{1,3}\.?[0-9]{0,4})", line)
					if match != []:

						n = float(match[0][1])
						w = float(match[0][0])

						wm = w % 10
						nm = n % 10

						wM = (int(w) - wm) / 10
						nM = (int(n) - nm) / 10

						if nm == 0:
							wm += 1

						tile = wm * 10 + nm

						if abs(n) > 80:
							if n > 0:
								world = 1
							else:
								world = 2
						else:
							rows = 0
							while nM > -8:
								rows += 1
								nM -= 1

							world = 2 + 36 * rows + wM + 18

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
		print("usage: build <project> [OPTIONS]")
		print("Builds the tiles with osm2city")
		print("")
		print("OPTIONS")
		print("  -h, --help      Shows this help and exit")
		print("  -p, --progress  Shows progress and exit")
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

run("mkdir -p projects/worldbuild/output/error")

def build_tile(name, west, south, east, north):
	if west < 0:
		west = "*" + str(west)
	else:
		west = str(west)
	south = str(south)
	east = str(east)
	north = str(north)

	run("./read-pbf worldbuild " + pbf_path + name + ".osm.pbf")
	run('echo "bounds=' + west + "_" + south + "_" + east + "_" + north + '" > projects/settings')
	run("./build worldbuild --chunk-size 5")

def after_build(name):
	if os.path.isfile("projects/worldbuild/osm2city-exceptions.log"):
		run("mv projects/worldbuild/osm2city-exceptions.log projects/worldbuild/output/error/" + name + ".exceptions.log")
		run("zip -rq projects/worldbuild/output/error/" + name + ".zip projects/worldbuild/scenery/ ")

		# Trigger failed after build script
		if os.path.isfile("./scripts/afterbuild-failed.sh"):
			os.system("./scripts/afterbuild-failed.sh &")
	else:
		run("zip -rq projects/worldbuild/output/" + name + ".zip projects/worldbuild/scenery/ ")

		# Trigger after build script
		if os.path.isfile("./scripts/afterbuild-success.sh"):
			os.system("./scripts/afterbuild-success.sh &")

	run("rm -r projects/worldbuild/scenery/*")
	run("./clear-cache-files worldbuild")

def prepare():
	run("./delete-db worldbuild")
	run("./create-db worldbuild")

def run_all(name, w, s, e, n):
	prepare()
	build_tile(name, w, s, e, n)
	after_build(name)

def norm(num, length):
	num = str(num)
	while len(num) < length:
		num = "0" + num
	return num

# Build poles first
run_all("n-pole", -180, 80, 180, 90)
run_all("s-pole", -180, -90, 180, -80)

for i in range(-7, 9):
	i *= 10
	for j in range(-18, 18):
		j *= 10
		if i >= 0:
			ns = "n"
		else:
			ns = "s"
		if j >= 0:
			ew = "e"
		else:
			ew = "w"

		name = ew + norm(abs(j), 3) + ns + norm(abs(i), 2)

		run_all(name, j, i, j + 10, i + 10)




