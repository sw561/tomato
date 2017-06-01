from tomato import get_home
import matplotlib.pyplot as plt
from numpy import arange
import logging

def plot(day, week):
	"""Plot sessions of the day"""

	starts = []
	widths = []
	for s in day.sessions:
		# Convert session starts, and durations to hours
		try:
			start = s.toggles[0].hour + s.toggles[0].minute/60.
			width = s.duration().seconds/(60.*60)
		except IndexError:
			pass
		else:
			# Append in else clause to ensure the lists remain the same length
			# as each other
			starts.append(start)
			widths.append(width)

	logging.info("Plotting the day")
	logging.info("Starts are %s" % str(starts))
	logging.info("Durations are %s" % str(widths))

	fig = plt.figure()
	fig.set_size_inches(6,7)
	fig.subplots_adjust(top=0.95,bottom=0.05,left=0.1,
		right=0.95, hspace=0.3)

	plt.subplot(2,1,1)
	plt.bar(starts, [1 for i in starts], width=widths)

	plt.yticks([])
	plt.ylim([-1,2])
	if starts:
		plt.xlim([min(9, starts[0]), max(18, starts[-1]+widths[-1])])
	else:
		plt.xlim([9, 18])
	plt.xlabel("Hour of the day")
	plt.title("%s: %.1f hours" \
		% (day.date.strftime("%A"), day.total_time().seconds/(60.*60))
		)

	logging.info("Plotting the week")

	heights = [(i.work_time.seconds/(60.*60)) if i is not None else 0 \
		for i in week.days]

	plt.subplot(2,1,2)
	plt.bar(range(7), heights, width=1)

	plt.xlim([0,7])
	plt.xticks(arange(0.5, 7),
		[i.date.strftime("%a") if i is not None else "" for i in week.days]
		)
	plt.tick_params(top='off',bottom='off')
	plt.ylabel("Hours")

	# Need to convert total time to hours (may be over one day)
	total = week.total_time()
	hours = total.days*24 + total.seconds/(60.*60)
	plt.title("Week total: %.1f hours" % hours)

	plt.savefig(get_home()+"/tomato/report.png")
	plt.clf()
