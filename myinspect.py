#!/usr/bin/env python

import shelve
import logging
from main import unshelve,reshelve,write_data
from datetime import *
import os
from renumber import renumber
from tomato import plan_path
from yesno import yes_no_question

# Implement a rudimentary interpretor

logging.basicConfig(
	format="%(asctime)s %(levelname)s : %(message)s",
	level=logging.INFO,
	datefmt="%-H:%M:%S"
)

day, week = unshelve()
session = day.get_session()

def toggle(hour=None, minute=0):
	if hour is None:
		session.toggle()
	else:
		now = datetime.now()
		time = datetime(now.year, now.month, now.day, hour, minute)
		session.toggle(time)
	show()
	save_prompt()

def remove(n):
	session.toggles.pop(n)
	show()
	save_prompt()

def save_prompt():
	print "Do you want to save the changes?"
	if yes_no_question():
		save()

def save():
	reshelve(day, week)
	write_data(session)

def show():
	session.log()
	print ""
	print "To add a toggle use toggle(hour, minute)"
	print "To remove a toggle use remove(n), as indicated by #"
	print "To save the toggles use save()"
	print ""
	print "To display the plan use plan()"

def plan():
	renumber(plan_path())
	with open(plan_path(),"r") as f:
		for line in f: print line.strip()
	print "\nTo edit the plan use edit_plan()"

def edit_plan():
	os.system("vim %s" % plan_path())
	plan()

print ""
show()
