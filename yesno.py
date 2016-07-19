def yes_no_question():
	while True:
		print(" [y/n] ")
		text = raw_input()
		if text.lower().startswith("y"):
			return True
		elif text.lower().startswith("n"):
			return False
		else:
			print("Sorry, I didn't understand that. Please type yes or no.")
