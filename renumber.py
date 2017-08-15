import sys

def renumber(name):
	"""
	Redo the numbering on a list stored in the file name
	"""
	# Load the items in to memory as tuples (n,item)
	items = []
	with open(name,"r") as f:
		for line in f:
			if not line.strip():
				continue
			index_open = line.find('(')
			index = line.find(')')
			if index==-1 or 0 <= index_open < index:
				# Line not numbered. Append to previous entry
				if not items:
					raise ValueError("First entry not numbered")
				(a, b) = items[-1]
				items[-1] = (a, "{}\n    {}".format(b, line.strip()))
				continue

			first_letter = index+1
			while first_letter < len(line) and not line[first_letter].isalpha():
				first_letter += 1
			a = line[:index].strip()
			b = line[first_letter:].strip()
			if a!="x" and b:
				items.append((float(a),b))

	items.sort(key=lambda x: x[0])

	# If everything is ok, rewrite the file with 1 based integers
	with open(name,"w") as f:
		for i, (_,b) in enumerate(items, start=1):
			if i>1: f.write("\n")
			f.write("{:2}) {}\n".format(i, b))

if __name__=="__main__":
	name = sys.argv[1]
	renumber(name)
