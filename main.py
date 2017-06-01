#!/usr/bin/env python

import argparse
import logging
import shelve
from datetime import datetime, timedelta
from time import sleep
import os
from session import Day, Week, WorkDay
from plotter import plot
from tomato import tmux_format, tmux_format_monitor,\
	data_file_path, shelf_path, max_lag, monitor_file_path
import lag

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
		logging.info("The data_file %s was not found" % data_file_path())
		return ""

	now = datetime.now()
	x = imp-now
	# Only print if the session is recent
	logging.info("Status, x: %d %s" % (status, str(x)))
	if status or x>timedelta(0, -60*60):
		return tmux_format(status, x)
	else:
		logging.info("The session is old - not printing")
		return ""

def log_string():

	# Work out if log files are being actively updated
	try:
		with open(monitor_file_path(), 'r') as f:
			log_folder = f.read().strip()
	except IOError:
		logging.info("Could not open monitor_file_path: %s" % monitor_file_path())
		return ""

	logging.info("Checking log activity in folder %s" % log_folder)
	try:
		lag_time = lag.lag(log_folder)
	except lag.BadCommand:
		logging.info("Bad command, probably indicates folder is invalid path")
		return ""

	logging.info("Lag found to be %s" % str(lag_time))
	max_time = max_lag()
	logging.info("Max lag is %s" % str(max_time))
	log_status = lag_time.total_seconds() < max_time
	# Get log_name to put in tmux status line
	if log_folder[-1]=="/":
		log_name = log_folder.split("/")[-2]
	else:
		log_name = log_folder.split("/")[-1]
	logging.info("Log name is %s" % log_name)
	return tmux_format_monitor(log_status, log_name)

def write_data(session):
	if not session.toggles:
		return
	# Write the important time and status to file
	# This is the information which is needed by the tmux_string function
	with open(data_file_path(), "w") as f:
		# This is a string "ON" or otherwise, and a space separated list of
		# integers representing the date: year, month, day, hour, minute,
		# second
		status = session.status()
		imp = session.important_time()
		if status: st="ON"
		else: st="OFF"
		f.write("%s" % st + imp.strftime(" %Y %m %d %H %M %S") + "\n")

def unshelve():
	d = shelve.open(shelf_path())
	today = datetime.now().date()
	day = d.get("day", Day(today))
	week = d.get("week", Week())

	if day.date!=today and not day.last_session().status():
		# Save data from old day in week object
		week.add_day(WorkDay(day))
		week.clean()
		d["week"] = week

		# Make a new day instance
		day = Day(today)
		logging.info("Making a new day %s" % day.date)

	d.close()
	return day,week

def reshelve(day, week):
	d = shelve.open(shelf_path())
	d["week"] = week
	d["day"] = day
	d.close()

def use_shelf(g):
	# A decorator for functions that unshelve and reshelve
	def f():
		day,week = unshelve()
		g(day, week)
		reshelve(day, week)
	return f

def set_log_folder(log_folder):
	with open(monitor_file_path(), 'w') as f:
		f.write(log_folder+"\n")

@use_shelf
def toggle(day, week):
	session = day.get_session(interactive=False)
	session.toggle()
	session.log()
	write_data(session)

if __name__=="__main__":
	parser = argparse.ArgumentParser(
		description=
"""
Tomato is an implementation of a pomodoro app for the status bar in tmux
"""
		)
	parser.add_argument("-v", "--verbose", action="store_true",
	                    help="verbose output for debugging"
	                    )
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-t", "--toggle", action="store_true",
	                   help="Toggle the working status of the app"
	                   )
	group.add_argument("-q", "--quiet", action="store_true",
	                   help="Stop reporting tomato time"
	                   )
	group.add_argument("-r", "--report", action="store_true",
	                   help="Create plot which reports on recent work patterns"
	                   )
	group.add_argument("-x", "--tmux", action="store_true",
	                   help="Output string for use in tmux status bar"
	                   )
	group.add_argument("-m", "--monitor", nargs=1, action="store", type=str,
	                   metavar="path",
	                   help="Monitor a folder for activity"
	                   )
	args = parser.parse_args()
	if args.verbose:
		logging.basicConfig(
			format="%(asctime)s %(levelname)s : %(message)s",
			level=logging.INFO,
			datefmt="%-H:%M:%S"
		)

	if args.tmux:
		# Sleep a while, so the toggle operation has a chance to complete
		if not args.verbose:
			sleep(0.5)
		tmux_string()

	elif args.toggle:
		toggle()

	elif args.quiet:
		os.remove(data_file_path())

	elif args.report:
		day,week = unshelve()
		plot(day, week)

	elif args.monitor is not None:
		print "Setting folder to monitor to be: %s" % args.monitor[0]
		set_log_folder(args.monitor[0])

	else:
		print "Doing nothing..."
		print "Run './main.py --help' for help with options"
