import matplotlib.pyplot as plt
from numpy import arange
import logging

def plot_day(day):
	"""Plot sessions of the day"""

	starts = []
	widths = []
	for s in day.sessions:
		# Convert session starts, and durations to hours
		starts.append(s.toggles[0].hour + s.toggles[0].minute/60.)
		widths.append(s.duration().seconds/(60.*60))

	logging.info("Plotting the day")
	logging.info("Starts are %s" % str(starts))
	logging.info("Durations are %s" % str(widths))

	fig = plt.figure()
	fig.set_size_inches(6,3)
	fig.subplots_adjust(top=0.85,bottom=0.2,left=0.02,
		right=0.99)

	plt.bar(starts, [1 for i in starts], width=widths)

	ax = plt.subplot(1,1,1)

	plt.yticks([])
	plt.ylim([-1,2])
	plt.xlim([9, starts[-1]+widths[-1]])
	plt.xlabel("Hour of the day")

	plt.title("Total time: %.1f hours" % (day.total_time().seconds/(60.*60)))

	plt.savefig("day.png")
	plt.clf()

def plot_week(week):
	logging.info("Plotting the week")

	fig = plt.figure()
	fig.set_size_inches(6,4)
	fig.subplots_adjust(top=0.85,bottom=0.2,left=0.1,
		right=0.99)

	heights = [(i.work_time.seconds/(60.*60)) if i is not None else 0 \
		for i in week.days]

	plt.bar(range(7), heights, width=1)

	plt.xlim([0,7])
	plt.xticks(arange(0.5, 7),
		[i.date.strftime("%a") if i is not None else "" for i in week.days]
		)
	plt.ylabel("Hours")

	plt.title("Total time: %.1f" % (week.total_time().seconds/(60.*60)))

	plt.savefig("week.png")
	plt.clf()
