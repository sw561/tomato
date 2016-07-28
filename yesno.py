def yes_no_question(question):
	print("%s ([y]/n)" % question)
	text = raw_input()
	if text.lower().startswith("n"):
		return False
	else:
		return True
