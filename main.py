from pysvg.filter import *
from pysvg.gradient import *
from pysvg.linking import *
from pysvg.script import *
from pysvg.shape import *
from pysvg.structure import *
from pysvg.style import *
from pysvg.text import *
from pysvg.builders import *
from pysvg.parser import parse

import json
import argparse
import os
from termcolor import cprint
import time

import helpers
import png_renderer
import legend
import labels

def style_order_helper():
	global style_order

	style_order = []
	for styl in styles['label']:
		style_order.append(styl)

def order_chooser(elems, order):
	if (order == "regular"):
		return(elems)
	elif (order == "reversed"):
		return(reversed(elems))
	else:
		raise Exception("order needs to be 'regular' or 'reversed'")

def style_sort(k):
	return (style_order.index(k['style']))

def styles_in_sheet_helper():
	pass

def load_pins_file(filepath, svg):
	f = open(filepath)
	board_data = json.load(f)
	f.close()

	global legend_data
	legend_data = board_data["legend"]
	
	filename = os.path.splitext(os.path.basename(filepath))[0]
	board = G(**helpers.kwargs_helper([("id", filename)]))

	for index, pin_group in enumerate(board_data["groups"]):
		group_name = filename + "_" + str(index) + "_" + pin_group["name"]
		group = G(**helpers.kwargs_helper([("id", group_name)]))

		units = "px"
		if ("units" in pin_group["origin"]):
			units = pin_group["origin"]["units"]
		
		x = helpers.units_to_pixels(pin_group["origin"]["x"], units)
		y = helpers.units_to_pixels(pin_group["origin"]["y"], units)
		
		#adding all the syles encountered in a list for the legend excluding the omited categories
		for pind in pin_group["pins"]:
			for func in pind["functions"]:
				if ("categories" in func) and any(check in func["categories"] for check in omit_categories):
					pass
				elif (func["style"] not in styles_in_sheets):
					styles_in_sheets.append(func["style"]) 

		#choosing the order (from top to bottom aka regular or from bottom to top aka reversed)
		order="regular"
		if ("order" in pin_group):
			order = pin_group["order"]

		#sort the pins with their style
		for pind in pin_group["pins"]:
			pin_functions = pind["functions"]
			pin_functions.sort(key=style_sort) #sort the label within pin with the order of the styles in the style.json

		#make the pin
		for b in order_chooser(pin_group["pins"], order):
			labels.pin_maker(b, group, x, y, pin_group["side"], styles, omit_styles, omit_categories)

			spacing = helpers.inch_to_pixels(0.1)
			if ("spacing" in pin_group):
				spacing = pin_group["spacing"]
				
			y = y + helpers.mm_to_pixels(spacing)
		board.addElement(group)
	svg.addElement(board)
# def categories_helper(filepath_array):
#	 for (filepath in filepath_array):
#		 f = open(filepath)
#		 board_data = json.load(f)
#		 f.close()
#		 for group in board_data["groups"]:
#			 for f in pin_data['functions']:


if __name__ == '__main__': 
	start = time.time()

	global styles #all the styles in the json style file
	global categories #all the categories in the json pin file
	global omit_categories
	global sheet_name
	global styles_in_sheets

	styles_in_sheets = []

	s = Svg(0, 0, helpers.mm_to_pixels(297), helpers.mm_to_pixels(210)) #TODO: auto choose the size of the canvas
	# A4 paper = 210 x 297 mm

	all_args = argparse.ArgumentParser()

	all_args.add_argument('-p', "--pins", action='append', required=True, help="pins.json file(s)")
	all_args.add_argument("-s", "--style", required=False, help="style.json file")
	all_args.add_argument('-os', "--omit_styles", action='append', required=False, help="prevent plotting of a style")
	all_args.add_argument('-oc', "--omit_categories", action='append', required=False, help="prevent plotting of a category")
	all_args.add_argument("-l", "--legend", action='store_true', required=False, help="plotting the legend")
	all_args.add_argument("-w", "--show", action='store_true', required=False, help="show a preview png file (not 100% accurate).")
	all_args.add_argument('-i', "--inkscape", action='store_true', required=False, help="open inkscape")
	all_args.add_argument("-o", "--output", required=False, help="name of the output file (pinout.svg is the default value)")

	args = vars(all_args.parse_args())
	#print(args)
	style_file = 'styles.json'
	if (args['style']):
		style_file = args['style']

	fstyles = open(style_file)
	styles = json.load(fstyles)
	fstyles.close()

	omit_categories = []
	omit_styles = []

	# omit_styles = ["portPin", "default", "led", "timer", "adc", "dac", "i2c", "spi", "audio", "control", "jtag", "usb", "rtc"] #["timer"]

	if (args['omit_styles']):
		for omit_styles_arg in args['omit_styles']:
			if (omit_styles_arg not in styles['label']):
				cprint("Warning: '" + omit_styles_arg + "' is not present in the style file. skipping", "yellow")
			else:
				omit_styles.append(omit_styles_arg)

	if (args['omit_categories']):
		for omit_categories_arg in args['omit_categories']:
			omit_categories.append(omit_categories_arg)
		#TODO: check if the category exist

	style_order_helper()
	for pin_file in args['pins']:
		load_pins_file(pin_file, s)

	if (args['legend']):
		legend.legend_maker(s, styles, omit_styles, omit_categories, legend_data, styles_in_sheets)


	output_file = "pinout.svg"
	if (args['output']):
		output_file = str(args['output'])

	s.save(output_file)
	end = time.time()
	cprint("Done in %.3f"%(end - start) + "s ! Happy pin making :)", "green")

	if (args['show']):
		cprint("Opening the rendered png file ,..", "blue")
		png_renderer.show_svg(output_file, s.get_width(), s.get_height())

	if (args['inkscape']):
		if (helpers.is_tool("inkscape")):
			cprint("Opening inkscape ...", "blue")
			os.system("inkscape " + output_file + " 2> /dev/null &") #quiet please
		else:
			helpers.inkscape_not_here_helper()
