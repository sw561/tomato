from datetime import *
from tomato import tomato, potato, max_work
import logging

class Year(object):
	def __init__(self):
		self.weeks = [0]*54
		self.year = datetime.now().year

	def log(self):
		logging.info("Printing a year")
		for i,w in enumerate(self.weeks):
			logging.info("Week %d: %.2f" % (i, w))

	def add_day(self, workday):
		week = int(workday.date.strftime("%W"))
		self.weeks[week] += workday.work_time.seconds/(60.*60)

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

	def get_session(self):
		if not self.sessions or self.sessions[-1].stale():
			logging.info("Creating a new session")
			self.sessions.append(Session())
		else:
			logging.info("Returning a session which started: %s"\
				% str(self.sessions[-1].toggles[0])
				)
		return self.sessions[-1]

	def total_time(self):
		return sum([x.duration() for x in self.sessions], timedelta())

class Session(object):
	def __init__(self):
		self.toggles = []

	def log(self):
		logging.info("Printing a session")
		for i in self.toggles:
			logging.info("%s" % str(i))
		logging.info("Finished printing a session")

	def status(self):
		# Odd number of toggles means working
		return len(self.toggles)%2

	def toggle(self):
		t = datetime.now()
		logging.info("Adding a toggle at time %s" % str(t))
		self.toggles.append(t)

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

		return (self.status(), imp_time)

	def stale(self):
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
