# A module to find the amount of time since the last
# file modification in folder passed as a command line argument

from datetime import datetime, timedelta
from subprocess import check_output
import logging
from os import stat

class BadCommand(Exception):
	pass

def get_last_modification_time(folder):
	""" Get time of last file modification in the given folder """
	command = "cd %s && " % folder
	command += "find . -maxdepth 1 -not -type d -and -not -name '.*'"
	command += " | xargs ls -tr | tail -n 1"
	try:
		newest_file = check_output(command, shell=True).strip()
	except:
		logging.info("Command is: %s" % command)
		raise BadCommand
	s = stat("%s/%s" % (folder,newest_file))
	d = datetime.fromtimestamp(s.st_mtime)
	return d

def lag(folder):
	""" Get time since last file modification in the given folder """
	d = get_last_modification_time(folder)
	now = datetime.now()
	return now-d
