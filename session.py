from datetime import *
from tomato import tomato, potato, max_work
import logging
from yesno import yes_no_question

class Week(object):
	def __init__(self):
		self.days = [None]*7

	def log(self):
		logging.info("Printing a week")
		for i in self.days:
			if i is not None:
				logging.info("%s %d/%d %.2f" \
					% (i.date.strftime("%a"), i.date.month, i.date.day,
						i.work_time.seconds/(60*60.)
						)
					)
		logging.info("Finished printing a week")

	def add_day(self, workday):
		slot = workday.date.weekday()
		self.days[slot] = workday
		logging.info("Adding workday from %d/%d in slot %d" \
			% (workday.date.month, workday.date.day, slot)
			)

	def clean(self):
		"""Remove days that are older than a week"""
		logging.info("Checking week for old days")
		today = datetime.now().date()
		for i,d in enumerate(self.days):
			if d is not None and today-d.date > timedelta(7):
				self.days[i] = None
				logging.info("Deleting old workday from %d/%d in slot %d" \
					% (d.date.month, d.date.day, i)
					)

	def total_time(self):
		return sum([x.work_time for x in self.days if x is not None],
			timedelta())

class WorkDay(object):
	"""
	A minimalist day - just the date and total work time, for use in Week
	"""
	def __init__(self, day):
		self.date = day.date
		self.work_time = day.total_time()

class Day(object):
	def __init__(self, date):
		self.date = date
		self.sessions = []

	def log(self):
		for s in self.sessions:
			s.log()

	def new_session(self):
		logging.info("Creating a new session")
		self.sessions.append(Session())
		return self.sessions[-1]

	def last_session(self):
		s = self.sessions[-1]
		if not s.toggles:
			logging.info("Returning an empty session")
		else:
			logging.info("Returning a session which started: %s"\
				% str(s.toggles[0])
				)
		return s

	def get_session(self, interactive=True):
		if not self.sessions:
			return self.new_session()

		elif self.sessions[-1].stale():
			if not interactive:
				return self.new_session()
			else:
				print "Session is stale"
				print "Do you want to create a new session?"
				if yes_no_question():
					return self.new_session()
				else:
					return self.last_session()

		else:
			return self.last_session()

	def total_time(self):
		return sum([x.duration() for x in self.sessions], timedelta())

class Session(object):
	def __init__(self):
		self.toggles = []

	def log(self):
		logging.info("Printing a session")
		on = True
		for (n,i) in enumerate(self.toggles):
			logging.info("#%d: %s" % (n,str(i)))
			if on:
				logging.info("\tWORK")
			else:
				logging.info("\tBREAK")
			on = not on
		# Only print important time if there is at least one toggle
		if self.toggles:
			logging.info("Imp Time: %s" % str(self.important_time()))
		logging.info("Finished printing a session")

	def status(self):
		# Odd number of toggles means working
		return len(self.toggles)%2

	def toggle(self, t=None):
		if t is None:
			t = datetime.now()
			should_sort = False
		else:
			should_sort = True
		logging.info("Adding a toggle at time %s" % str(t))
		self.toggles.append(t)

		if should_sort:
			# Insertion sort for the new toggle to keep the list sorted
			t = self.toggles
			for n in xrange(len(t)-1,0,-1):
				if t[n]>t[n-1]: break
				t[n], t[n-1] = t[n-1], t[n]

	def important_time(self):
		"""
		Return the status and critical time required for the tmux output.
		Variables ending in _s are integers representing time intervals in
		seconds.
		"""
		work_s = self.work_time().seconds
		break_s = self.break_time().seconds
		if self.status():
			st = "ON"
			remaining_time_s = tomato(work_s, break_s)
		else:
			st = "OFF"
			remaining_time_s = potato(work_s, break_s)

		imp_time = datetime.now() + timedelta(0, remaining_time_s)
		return imp_time

	def stale(self):
		if not self.toggles:
			return False
		if self.status():
			# If currently working, then the session is not stale
			s = False
		else:
			# If tomato time is unacceptably long, it is stale
			t = tomato(self.work_time().seconds, self.break_time().seconds)
			logging.info("Evaluating tomato to check staleness")
			logging.info("Tomato was found to be %d mins" % (t/60))
			s = t > max_work()

		logging.info("Session staleness was found to be %d" % s)
		return s

	def break_time(self):
		"""Amount of break time in the session so far"""
		s = timedelta()
		for i in xrange(1, len(self.toggles)-1, 2):
			s += self.toggles[i+1] - self.toggles[i]

		# If not working need to add the last period of time
		if not self.status():
			s += datetime.now() - self.toggles[-1]
		return s

	def work_time(self):
		return self.length() - self.break_time()

	def duration(self):
		"""The time between session start and last piece of work"""
		if self.status():
			# Currently on, return time since session was started
			return self.length()
		else:
			# Otherwise return time until last bit of work
			return self.toggles[-1] - self.toggles[0]

	def length(self):
		"""Just the time since the session was started"""
		return datetime.now() - self.toggles[0]
