#!/usr/bin/env python

import shelve
import logging
from main import unshelve,reshelve,write_data
from datetime import *

# Implement a rudimentary interpretor

logging.basicConfig(
	format="%(asctime)s %(levelname)s : %(message)s",
	level=logging.INFO,
	datefmt="%-H:%M:%S"
)

day, week = unshelve()
session = day.get_session(interactive=True)

def toggle(hour=None, minute=0):
	if hour is None:
		session.toggle()
	else:
		now = datetime.now()
		time = datetime(now.year, now.month, now.day, hour, minute)
		session.toggle(time)
	show()

def remove(n):
	session.toggles.pop(n)
	show()

def save():
	reshelve(day, week)
	write_data(session)

def prompt():
	print "To add a toggle use add_toggle(hour, minute)"
	print "To remove a toggle us remove(n), as indicated by #"
	print "To save the toggles use save()"

def show():
	session.log()
	print ""
	prompt()

show()
