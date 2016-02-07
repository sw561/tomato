import matplotlib.pyplot as plt
import logging

def plot_day(day):
	"""Plot sessions of the day"""

	starts = []
	widths = []
	for s in day.sessions:
		s.log()
		# Convert session starts, and durations to hours
		starts.append(s.toggles[0].hour + s.toggles[0].minute/60.)
		widths.append(s.duration().seconds/(60.*60))

	logging.info("Starts are %s" % str(starts))
	logging.info("Durations are %s" % str(widths))

	fig = plt.figure()
	fig.set_size_inches(6,3)
	fig.subplots_adjust(top=0.85,bottom=0.2,left=0.01,
		right=0.99)

	plt.bar(starts, [1 for i in starts], width=widths)

	ax = plt.subplot(1,1,1)
	ax.spines['right'].set_visible(False)
	ax.spines['left'].set_visible(False)

	plt.yticks([])
	plt.ylim([-1,2])
	plt.xlim([9, starts[-1]+widths[-1]])
	plt.xlabel("Hour of the day")

	plt.title("Total time: %.1f hours" % (day.total_time().seconds/(60.*60)))

	plt.savefig("day.png")
