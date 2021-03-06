# This module defines how much work and break the app will recommend. It also
# defined the formatting used in the tmux status bar and the paths of data
# files which are used to log your working hours
#
# Note that all algebra in this module is done in seconds.
#
import os

def max_work():
	"""
	The amount of seconds of work above which the session is considered to be
	stale.
	"""
	return 60*60

def break_length():
	"""
	The chosen break length, if you start your break as early as possible
	"""
	return 6*60

def ratio():
	""" Ratio of work to break time """
	return 4

def offset():
	"""
	If you like to add extra minutes to the first pomodoro of your session, do
	so by setting a non-zero offset.
	"""
	return ratio()*break_length()

def tomato(work_s, break_s):
	"""
	Amount more work required such that that a break has been earned

	find amount of work, x, such that
		work + x = (break+bl)*r + o
	"""
	return (break_s+break_length()) * ratio() + offset() - work_s

def potato(work_s, break_s):
	"""
	Amount of break time allowed until need to start working

	find amount of break, x, such that
		r*(break + x) + o = work
	"""
	return (work_s - offset())/ratio() - break_s

def tmux_format(working, x):
	"""
	A function for formatting the output for the tmux status bar.
	working is a boolean, x is timedelta until important time
	"""
	if working and x.days>=0:
		message = "KW"
		r = "reverse"
		fg = "colour4"
		bg = "white"

	elif working and x.days<0:
		message = "HB"
		r = "noreverse"
		fg = "black"
		bg = "yellow"

	elif not working and x.days>=0:
		message = "EB"
		r = "noreverse"
		fg = "black"
		bg = "green"

	elif not working and x.days<0:
		message = "GW"
		r = "reverse"
		fg = "colour1"
		bg = "white"

	s = "#[%s,fg=%s,bg=%s]  %s" % (r, fg, bg, message)

	if x.days>=0:
		n = x.seconds/60+1
		if n==1:
			s += ": %d min" % n
		else:
			s += ": %d mins" % n

	return s+"  "

def max_lag():
	""" Max seconds of lag in log file update """
	return 180

def tmux_format_monitor(log_status, log_name):
	message = log_name
	if log_status:
		fg = "black"
		bg = "white"
		reverse = "noreverse"
		message += "  "
	else:
		message += "  |"
		fg = "white"
		bg = "default"
		reverse = "noreverse"
	s = "#[%s,fg=%s,bg=%s]  %s" % (reverse, fg, bg, message)
	return s

def get_home():
	"""Return home directory for the current computer"""
	return os.path.expanduser("~")

def data_file_path():
	return get_home()+"/Dropbox/status.txt"

def shelf_path():
	return get_home()+"/Dropbox/tomato.db"

def plan_path():
	return get_home()+"/Dropbox/plan"

def monitor_file_path():
	return get_home()+"/tomato/monitor_path"

if __name__=="__main__":
	print "File paths"
	print data_file_path()
	print shelf_path()

	print "Sample tomato, potatoes"
	for f in [tomato, potato]:
		for break_time in [0,3,6]:
			print "%d break" % break_time
			for work_time in [0,24,48,60]:
				print f(work_time*60, break_time*60)/60
