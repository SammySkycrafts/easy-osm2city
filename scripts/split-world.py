#! /usr/bin/python
import os
import sys

config_path = os.path.dirname(os.path.realpath(__file__)) + "/osmium-config/"
prefix = "osmium-cut-world-step-"
world_file = sys.argv[1]
state4 = ['nw', 'ne', 'sw', 'se']
state2 = ['s', 'n']

def run_cut(path, step, name, start_file=None):
	if start_file != None:
		print("Splitting world in 4...")
		ret = os.system("osmium extract -c " + path + name + ".json " + start_file + " --overwrite")
		if ret == 0:
			os.system("mv n-pole.osm.pbf output/")
			os.system("mv s-pole.osm.pbf output/")
	else:
		print("Building: " + name + "...")
		os.system("osmium extract -c " + path + str(step) + "-" + name + ".json " + name + ".osm.pbf --overwrite")

run_cut(config_path + prefix, 1, "1", world_file)
con_pre = config_path + prefix
for i in range(0, len(state4)):
	run_cut(con_pre, 2, state4[i])
	for j in range(0, len(state4)):
		run_cut(con_pre, 3, state4[i] + "-" + state4[j])
		for k in range(1, 4):
			run_cut(con_pre, 4, state4[i] + "-" + state4[j] + "-" + str(k))
			for l in range(0, len(state2)):
				run_cut(con_pre, 5, state4[i] + "-" + state4[j] + "-" + str(k) + "-" + state2[l])

print("Removing temporary files...")
os.systemc("rm n* s*")
