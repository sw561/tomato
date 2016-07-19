import sys
import operator

def renumber(name):
	"""
	Redo the numbering on a list stored in the file name
	"""
	# Load the items in to memory as tuples (n,item)
	items = []
	with open(name,"r") as f:
		for line in f:
			if line.strip():
				a,b = map(operator.methodcaller("strip"),line.split(")"))
				if a!="x":
					items.append((float(a),b))

	items.sort(key=operator.itemgetter(0))

	# If everything is ok, rewrite the file with 1 based integers
	with open(name,"w") as f:
		for i,(a,b) in enumerate(items):
			if i: f.write("\n")
			f.write("%d) %s\n" % ((i+1),b))

if __name__=="__main__":
	name = sys.argv[1]
	renumber(name)
