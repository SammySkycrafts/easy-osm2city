#! /usr/bin/python
import os
import sys

pbf_path = sys.argv[1]

# Expecting project
os.system("mkdir -p projects/worldbuild/output/error")

def build_tile(name, west, south, east, north):
	if west < 0:
		west = "*" + str(west)
	else:
		west = str(west)
	south = str(south)
	east = str(east)
	north = str(north)

	os.system("./read-pbf worldbuild " + pbf_path + name + ".osm.pbf")
	os.system('echo "bounds=' + west + "_" + south + "_" + east + "_" + north + '" > projects/settings')
	os.system("./build worldbuild -z")

def after_build(name):
	if os.path.isfile("projects/worldbuild/osm2city-exceptions.log"):
		os.system("mv projects/worldbuild/osm2city-exceptions.log projects/worldbuild/output/error/" + name + ".exceptions.log")
	else:
		os.system("mv projects/worldbuild/worldbuild.zip projects/worldbuild/output/" + name + ".zip")
	os.system("rm -r projects/worldbuild/scenery/*")
	os.system("./clear-cache-files worldbuild")

def prepare():
	os.system("./delete-db worldbuild")
	os.system("./create-db worldbuild")

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

for i in range(-8, 8):
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

		name = ew + norm(j, 3) + ns + norm(i, 2)

		run_all(name, j, i, j + 10, i + 10)




