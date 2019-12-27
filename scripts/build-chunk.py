#! /usr/bin/python3
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
import socket
import re

host = socket.gethostname()
port = 12345
prefix = ""

argc = len(sys.argv)
i = 1
first = 1
while i < argc:
	if sys.argv[i] == "--port":
		i += 1
		port = sys.argv[i]
	elif sys.argv[i] == "--host":
		i += 1
		host = sys.argv[i]
	elif sys.argv[i] == "-p" or sys.argv[i] == "--prefix":
		i += 1
		prefix = sys.argv[i]
	elif sys.argv[i] == "-h" or sys.argv[i] == "--help":
		print("usage:  build_chunk.py [OPTIONS]")
		print("Runs a single chunk build. Mainly handles status logging")
		print("")
		print("  -p, --prefix      Database prefix to use")
		print("      --host	Logger host")
		print("      --port	Logger port")
		print("  -h, --help	Shows this help and exit")
	else:
		if first == 1:
			first = 0
			name = sys.argv[i]
		else:
			print("Unknown option " + sys.argv[i])
			sys.exit(1)
	i += 1

def send_status(name, status):
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((host, port))
		sock.send((name + " " + status).encode())
		sock.close()
	except IOError:
		print("Unable to send status. Aborting...")
		sys.exit(1)

send_status(name, "started")

os.system("mkdir -p projects/worldbuild-" + name)

os.system("cp projects/worldbuild/params.ini projects/worldbuild-" + name + "/")

if name == "n-pole":
	bounds = "bounds=*-180_80_180_90"
	db_name = prefix + "n-pole"
elif name == "s-pole":
	bounds = "bounds=*-180_-90_180_-80"
	db_name = prefix + "s-pole"
else:
	match = re.match(r"([ew])(\d{3})([ns])(\d{2})", name)
	if match == None:
		print("ERROR: Invalid tile name")
		sys.exit(1)
	else:
		ew = match.group(1)
		ew_val = int(match.group(2))
		ns = match.group(3)
		ns_val = int(match.group(4))

		if ew == "w":
			ew_val *= -1
		if ns == "s":
			ns_val *= -1

		if ew_val < 0:
			bounds = "bounds=*"
		else:
			bounds = "bounds="

		bounds += str(ew_val) + "_" + str(ns_val) + "_" + str(ew_val + 10) + "_" + str(ns_val + 10)
		if ew_val % 10 != 0:
		    ew_val = ew_val - (ew_val % 10)

		if ns_val % 10 != 0:
		    ns_val = ns_val - (ns_val % 10)

		db_name = prefix + ew + str(abs(ew_val)) + ns + str(abs(ns_val))

os.system("sed -i 's/DB_NAME.*/DB_NAME = \"" + db_name + "\"/' projects/worldbuild-" + name + "/params.ini")

os.system("echo '" + bounds + "' > projects/worldbuild-" + name + "/settings")

os.system("./build -t 1 worldbuild-" + name)

if os.path.isfile("projects/worldbuild-" + name + "/osm2city-exceptions.log"):
	os.system("mv projects/worldbuild-" + name + "/osm2city-exceptions.log projects/worldbuild/output/error/" + name + ".exceptions.log")

os.system("sleep 60")

os.system("rm -rf projects/worldbuild-" + name)

send_status(name, "done")
