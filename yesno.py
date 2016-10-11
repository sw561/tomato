def yes_no_question(question, default=True):
	if default:
		suggest = "([y]/n)"
	else:
		suggest = "(y/[n])"
	print("%s %s" % (question,suggest))
	text = raw_input().strip()
	if text.lower().startswith("n"):
		return False
	elif text.lower().startswith("y"):
		return True
	else:
		return default
