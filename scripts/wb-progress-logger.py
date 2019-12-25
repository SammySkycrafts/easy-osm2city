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

import socket
import sys
import json
import os
import re

host = socket.gethostname()
port = 12345
verbose = False
sfile = "projects/worldbuild/status"

argc = len(sys.argv)
i = 1
while i < argc:
	if sys.argv[i] == "--port":
		i += 1
		port = int(sys.argv[i])
	elif sys.argv[i] == "--host":
		i += 1
		host = sys.argv[i]
	elif sys.argv[i] == "-v":
		verbose = True
	elif sys.argv[i] == "-f" or sys.argv[i] == "--file":
		i += 1
		sfile = sys.argv[i]
	elif sys.argv[i] == "-h" or sys.argv[i] == "--help":
		print("usage: wb-progress-logger.py [OPTIONS]")
		print("Logs progress of the worldbuild when run")
		print("with database strategies 'chunk' and 'mono'")
		print("")
		print("OPTIONS")
#		print("  -f, --file        Status file to use")
		print("  -v, --verbose     Verbose printouts")
		print("    , --host        hostname or interface to bind to")
		print("    , --port        Port to bind to")
		print("  -h, --help        Shows this help and exit")
	else:
		print("Unknown option " + sys.argv[i])
		sys.exit(1)
	i += 1

def norm(num, length):
	num = str(num)
	while len(num) < length:
		num = "0" + num
	return num

if os.path.isfile(sfile):
	try:
		with open(sfile) as json_data:
			state = json.load(json_data)
	except ValueError:
		print("ERROR: Invalid status file")
		sys.exit(1)
else:
	state = {}

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host, port))

sock.listen(5)
print("Up and running...")
try:
	while True:
		c, addr = sock.accept()
		msg = c.recv(128)
		c.close()
		name, status = msg.decode().split()
		if verbose:
			print(name + " set status to " + status)

		if status == "started" or status == "done":
			if name == "n-pole" or name == "s-pole":
				if not name in state:
					state[name] = {}
				state[name]["status"] = status
			else:
				match = re.match(r"([ew])(\d{3})([ns])(\d{2})", name)
				if match == None:
					print("WARNING: Recived status " + status + " from invalid tile '" + name + "'")
				else:
					ew = match.group(1)
					ew_val = int(match.group(2))
					ns = match.group(3)
					ns_val = int(match.group(4))

					ew_val_major = int(ew_val / 10) * 10
					if ew == "w":
						if ew_val_major != ew_val:
							ew_val_major += 10

					ns_val_major = int(ns_val / 10) * 10
					if ns == "s":
						if ns_val_major != ns_val:
							ns_val_major += 10

					name_major = ew + norm(ew_val_major, 3) + ns + norm(ns_val_major, 2)
					if not name_major in state:
						state[name_major] = {}
					if not name in state[name_major]:
						state[name_major][name] = {}
					state[name_major][name]["status"] = status
					if not "status" in state[name_major]:
						state[name_major]["status"] = "progress"
						if status == "started":
							state[name_major]["started"] = 1
							state[name_major]["done"] = 0
						else:
							state[name_major]["started"] = 0
							state[name_major]["done"] = 1
					else:
						state[name_major][status] += 1
						if status == "done":
							state[name_major]["started"] -= 1
						if state[name_major]["done"] == 100:
							state[name_major]["status"] = "done"

			try:
				with open(sfile, 'w') as f:
					json.dump(state, f, indent=4)
			except IOError:
				print("WARNING: Failed to write to file")
		else:
			print("WARNING: Invalid status '" + status + "' recived from " + name)

except KeyboardInterrupt:
	try:
		with open(sfile, 'w') as f:
			json.dump(state, f, indent=4)
	except IOError:
		print("WARNING: Failed to write to file")
	sock.close()
	print("Exiting...")
	sys.exit(0)
