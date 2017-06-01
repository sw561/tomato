#!/usr/bin/env python

import logging
from main import unshelve,reshelve,write_data
from datetime import datetime
import os
from renumber import renumber
from tomato import plan_path,data_file_path
from yesno import yes_no_question

logging.basicConfig(
	format="%(asctime)s %(levelname)s : %(message)s",
	level=logging.INFO,
	datefmt="%-H:%M:%S"
)

day, week = unshelve()
session = day.get_session()
save_required = False

def toggle(hour=None, minute=0):
	if hour is None:
		session.toggle()
	else:
		now = datetime.now()
		time = datetime(now.year, now.month, now.day, hour, minute)
		session.toggle(time)
	show(changed=True)

def remove(n):
	session.toggles.pop(n)
	show(changed=True)

def new_session():
	global session
	session = day.new_session()
	show(changed=True)

def save():
	reshelve(day, week)
	write_data(session)
	global save_required
	save_required = False

def quiet():
	os.remove(data_file_path())

def show(changed=False):
	session.log()
	global save_required
	if save_required:
		print "The session is unsaved - use save()"
	elif changed:
		if yes_no_question("Do you want to save the changes?"):
			save()
		else:
			save_required = True

def help():
	print "To view the toggles of the session call show()"
	print "To add a toggle use toggle(hour, minute=0)"
	print "To remove a toggle use remove(n), where n is indicated by #"
	print "To make a new session use new_session()"
	print ("To temporarily remove the message in tmux, use quiet(). "
		"(To reinstate just toggle)")
	print "To save the toggles use save()"
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
print ""
print "For help with commands call help()"
