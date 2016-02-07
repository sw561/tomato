#!/usr/bin/env python

import argparse
import logging
import shelve
from datetime import *
from time import sleep
from session import *
from plotter import plot_day
from tomato import tmux_format, data_file_path, shelf_path

def tmux_string():
	try:
		with open(data_file_path(), "r") as f:
			s = f.read().split()
			(status, imp) = ("ON"==s[0]), datetime(*map(int, s[1:]))
	except IOError:
		logging.info("The data_file %s does was not found" % data_file_path())
		exit()

	now = datetime.now()
	x = imp-now
	print tmux_format(status, x)

def main(args):
	if args.tmux:
		# Sleep a while, so the toggle operation has a chance to complete
		if not args.verbose:
			sleep(0.5)
		tmux_string()
		return

	d = shelve.open(shelf_path())

	today = datetime.now().date()

	# If the shelf already has a current day object, retrieve it
	day_stale = True
	if d.has_key("day") and d["day"].date==today:
		day_stale = False
		day = d["day"]
		logging.info("Retrieving day %s with %d sessions" \
			% (day.date, len(day.sessions)))

	if args.report:
		if not day_stale:
			plot_day(day)
		else:
			logging.info("No active day - quitting")

	if args.toggle:
		if day_stale:
			day = Day(today)
			logging.info("Making a new day %s" % day.date)

		session = day.get_session()
		session.toggle()
		session.log()

		# Reshelve the day
		d["day"] = day

		# Write the important time and status to file
		# This is the information which is needed by the tmux_string function
		with open(data_file_path(), "w") as f:
			# This is a string "ON" or otherwise, and a space separated list of
			# integers representing the date: year, month, day, hour, minute,
			# second
			(status, imp) = session.important_time()
			if status: st="ON"
			else: st="OFF"
			s =  st + imp.strftime(" %Y %m %d %H %M %S")
			f.write("%s\n" % s)

	d.close()

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
	                   help="Create plots which report on recent work patterns"
	                   )
	group.add_argument("--tmux", action="store_true",
	                   help="Output string for use in tmux status bar"
	                   )
	args = parser.parse_args()
	if args.verbose:
		logging.basicConfig(
			format="%(asctime)s %(levelname)s : %(message)s",
			level=logging.INFO,
			datefmt="%-H:%M:%S"
		)

	main(args)
