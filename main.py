#!/usr/bin/env python

import argparse
import logging
import shelve
from datetime import *
from time import sleep
from session import *
from plotter import *
from tomato import tmux_format, data_file_path, shelf_path

def tmux_string():
	try:
		with open(data_file_path(), "r") as f:
			s = f.read().split()
			(status, imp) = ("ON"==s[0]), datetime(*map(int, s[1:]))
	except IOError:
		logging.info("The data_file %s does was not found" % data_file_path())
		return

	now = datetime.now()
	x = imp-now
	# Only print if the session is recent
	logging.info("Status, x: %d %s" % (status, str(x)))
	if status or x>timedelta(0, -60*60):
		print tmux_format(status, x)
	else:
		logging.info("The session is old - not printing")

def write_data(session):
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

	if day.date!=today:
		# Save data from old day in week object
		week.clean()
		week.add_day(WorkDay(day))
		d["week"] = week

		# Make a new day instance
		logging.info("Making a new day %s" % day.date)
		day = Day(today)

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
	group.add_argument("-r", "--report", action="store_true",
	                   help="Create plot which reports on recent work patterns"
	                   )
	group.add_argument("-x", "--tmux", action="store_true",
	                   help="Output string for use in tmux status bar"
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

	elif args.report:
		day,week = unshelve()
		plot(day, week)
