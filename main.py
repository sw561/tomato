#!/usr/bin/env python

import argparse
import logging
import shelve
from datetime import datetime
import os
from session import Day, Week, WorkDay
from plotter import plot
from tomato import data_file_path, shelf_path, monitor_file_path
from tmux import tmux_string
from contextlib import contextmanager

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

@contextmanager
def use_shelf():
	# A decorator for functions that unshelve and reshelve
	day, week = unshelve()
	yield day, week
	reshelve(day, week)

def set_log_folder(log_folder):
	if not os.path.isdir(log_folder) and log_folder!="0":
		print "{} does not exist".format(log_folder)
		return
	with open(monitor_file_path(), 'w') as f:
		print "Setting folder to monitor to be: %s" % args.monitor[0]
		f.write(log_folder+"\n")

def toggle():
	with use_shelf() as (day, week):
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
		tmux_string()

	elif args.toggle:
		toggle()

	elif args.quiet:
		os.remove(data_file_path())

	elif args.report:
		day,week = unshelve()
		plot(day, week)

	elif args.monitor is not None:
		set_log_folder(args.monitor[0])

	else:
		print "Doing nothing..."
		print "Run './main.py --help' for help with options"
