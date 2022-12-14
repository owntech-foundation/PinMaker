from shutil import which
import platform
from termcolor import colored, cprint

def categories_helper(f):
	#TODO: add all categories to a list
	pass

def text_centerer_helper(em, elem, text):
	#1em = 0.08in height
	#1em = 6px char width
	em_width = em * 6
	em_height = em * inch_to_pixels(0.08)
	x = (elem[0] / 2) - ((len(text) * em_width) / 2)
	y = (elem[1] / 2) + (em_height / 2)

	return (x, y)

def kwargs_helper(attr_arr):
	kwargs={}

	for attr in attr_arr:
		kwargs[attr[0]] = attr[1]
	return kwargs

def intersection(lst1, lst2):
	lst3 = [value for value in lst1 if value in lst2]
	return lst3

def inch_to_pixels(inchs):
	return (inchs * 96)

def mm_to_pixels(mm): # 2.54 = 0.1 in
	return (inch_to_pixels(mm / 25.4))

def units_to_pixels(number, units="px"):
	if (units == "px"):
		return (number)
	elif (units == "mm"):
		return (mm_to_pixels(number))
	elif (units == "cm"):
		return (mm_to_pixels(number * 10))
	elif (units == "m"):
		return (mm_to_pixels(number * 1000))
	elif (units == "in"):
		return(inch_to_pixels(number))

def is_tool(name):
	"""Check whether `name` is on PATH and marked as executable."""

	return which(name) is not None

def inkscape_not_here_helper():
	cprint("Inkscape is not present in the PATH. Cannot open inkscape.", "red")
	my_os = platform.system()
	print("OS in my system : ",my_os)
	if (my_os == 'Darwin'):
		cprint("If you have Inkscape allready installed, try this command:" +
		"'export PATH=$PATH:/Applications/Inkscape.app/Contents/MacOS/'", "yellow")
	elif (my_os == 'Linux'):
		cprint("If you have Inkscape allready installed, try this command:" +
		"'export PATH=$PATH:<inkscape location>'", "yellow")
	elif (my_os == 'Windows'):
		cprint("If you have Inkscape allready installed, try to add the " +
		"folder where the .exe is located into the PATH of environment variables", "yellow")