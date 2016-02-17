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
	if status or x.days>=0 or (-x).seconds<60*60:
		logging.info("Status, x: %d %s" % (status, str(x)))
		print tmux_format(status, x)
	else:
		logging.info("Status, x: %d %s" % (status, str(x)))
		logging.info("The session is old - not printing")

def main(args):
	if args.tmux:
		# Sleep a while, so the toggle operation has a chance to complete
		if not args.verbose:
			sleep(0.5)
		tmux_string()
		return

	d = shelve.open(shelf_path())
	today = datetime.now().date()
	day = d.get("day", Day(today))
	week = d.get("week", Week())
	year = d.get("year", Year())

	if args.report:
		day.log()
		week.log()
		plot(day, week)
		if args.year:
			year.log()
			plot_year(year)

	if args.toggle:
		if day.date!=today:
			# Replace the day if it is stale, add old day to week
			wd = WorkDay(day)
			week.add_day(wd)
			d["week"] = week

			if year.year!=today.year:
				year = Year()
			year.add_day(wd)
			d["year"] = year

			day = Day(today)
			logging.info("Making a new day %s" % day.date)

		session = day.get_session()
		session.toggle()
		session.log()

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
			f.write("%s" % st + imp.strftime(" %Y %m %d %H %M %S") + "\n")

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
	group.add_argument("-x", "--tmux", action="store_true",
	                   help="Output string for use in tmux status bar"
	                   )
	parser.add_argument("-y", "--year", action="store_true",
	                   help="If using report option, plot the year too"
	                   )
	args = parser.parse_args()
	if args.verbose:
		logging.basicConfig(
			format="%(asctime)s %(levelname)s : %(message)s",
			level=logging.INFO,
			datefmt="%-H:%M:%S"
		)

	main(args)
