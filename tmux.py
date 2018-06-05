#!/usr/bin/env python

from logging import info
from datetime import datetime, timedelta
from tomato import data_file_path, tmux_format_monitor, monitor_file_path, max_lag, tmux_format
from subprocess import check_output, CalledProcessError

def tmux_string():
	s = ""
	s += tomato_string()
	s += log_string()
	print s

def tomato_string():
	try:
		with open(data_file_path(), "r") as f:
			s = f.read().split()
			(status, imp) = ("ON"==s[0]), datetime(*map(int, s[1:]))
	except IOError:
		info("The data_file %s was not found" % data_file_path())
		return ""

	now = datetime.now()
	x = imp-now
	# Only print if the session is recent
	info("Status, x: %d %s" % (status, str(x)))
	if status or x>timedelta(0, -60*60):
		return tmux_format(status, x)
	else:
		info("The session is old - not printing")
		return ""

def lag(folder):
	""" Get time since last file modification in the given folder """
	c1 = "date +%s"
	c2 = "find {} -maxdepth 2 -not -type d -and -name 'log.*'".format(folder)
	c2 += " | xargs ls -t | head -n 1 | xargs stat --format='%Y'"
	command = "expr $({}) - $({})".format(c1, c2)
	info("Command is: %s" % command)
	lag_time_seconds = check_output(command, shell=True).strip()
	return int(lag_time_seconds)

def log_string():
	# Work out if log files are being actively updated
	try:
		with open(monitor_file_path(), 'r') as f:
			log_folder = f.read().strip()
	except IOError:
		info("Could not open monitor_file_path: %s" % monitor_file_path())
		return ""

	if log_folder == "0":
		info("log_folder is 0, nothing to check")
		return ""

	info("Checking log activity in folder %s" % log_folder)
	try:
		lag_time = lag(log_folder)
	except CalledProcessError as e:
		if e.returncode == 1:
			# The expr program gives an exit-status of 1 if the result of the
			# expression is NULL or zero
			lag_time = int(e.output)
		else:
			info("Bad command, probably indicates folder is invalid path")
			return ""

	info("Type of lag_time is %s" % type(lag_time))
	info("Lag found to be %s" % str(lag_time))
	max_time = max_lag()
	info("Max lag is %s" % str(max_time))
	log_status = lag_time < max_time
	# Get log_name to put in tmux status line
	if log_folder[-1]=="/":
		log_name = log_folder.split("/")[-2]
	else:
		log_name = log_folder.split("/")[-1]
	info("Log name is %s" % log_name)
	info("Log status is %r" % log_status)
	return tmux_format_monitor(log_status, log_name)

if __name__=="__main__":
	tmux_string()
