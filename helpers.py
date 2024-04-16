from shutil import which
import platform
from termcolor import colored, cprint
import base64
import sys
import os, fileinput
import qrcode
import qrcode.image.svg
from copy import deepcopy

from pysvg.filter import *
from pysvg.gradient import *
from pysvg.linking import *
from pysvg.script import *
from pysvg.shape import *
from pysvg.structure import *
from pysvg.style import *
from pysvg.text import *
from pysvg.builders import *
# from pysvg.parser import parse
# from pysvg.parser import setAttributes
from pysvg_parser_patch import *

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

lineLabelList = [] #contains duplicates

def lineLabelNamer(pin_data):
	name = "lineLabel_" + pin_data["functions"][0]["name"]
	occurences = lineLabelList.count(name)
	lineLabelList.append(name)
	if (occurences > 0):
		name = name + "_" + str(occurences + 1) #if GND is present next group is GND_2

	return name

def labelFunctionNamer(s):
	try:
		return("label_" + s['name'].replace(" ", "_"))
	except KeyError:
		try:
			return("speLabel_" + s['special'].replace(" ", "_"))
		except KeyError:
			return("unknown")
	
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

paper_iso = [{"size":"4A0","wxh":[1682,2378]},{"size":"2A0","wxh":[1189,1682]},{"size":"A0","wxh":[841,1189]},{"size":"A1","wxh":[594,841]},{"size":"A2","wxh":[420,594]},{"size":"A3","wxh":[297,420]},{"size":"A4","wxh":[210,297]},{"size":"A5","wxh":[148,210]},{"size":"A6","wxh":[105,148]},{"size":"A7","wxh":[74,105]},{"size":"A8","wxh":[52,74]},{"size":"A9","wxh":[37,52]},{"size":"A10","wxh":[26,37]}]
def paper_size(input, orientation='Portrait'):
	formats_availables = "Availables formats: "
	for p in paper_iso:
		formats_availables+=(str(p["size"]) + " ")
		if p["size"] == input:
			if (orientation == 'Portrait'):
				return ({ "px": [mm_to_pixels(p["wxh"][0]), mm_to_pixels(p["wxh"][1])], "mm": [p["wxh"][0], p["wxh"][1]]})
			elif (orientation == 'Landscape'):
				return ({ "px": [mm_to_pixels(p["wxh"][1]), mm_to_pixels(p["wxh"][0])], "mm": [p["wxh"][1], p["wxh"][0]]})
			else:
				print("Page orientation " + str(orientation) + " is not supported")
				exit()
	print(formats_availables)
	exit()

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

licenses = [{"name": "cc-by-nc-nd.eu", "file": "licenses/by-nc-nd.eu.svg", "website": "https://www.creativecommons.org/licenses/by-nc-nd/4.0/"},
			{"name": "cc-by-nc-nd", "file": "licenses/by-nc-nd.svg", "website": "https://www.creativecommons.org/licenses/by-nc-nd/4.0/"},
			{"name": "cc-by-nc-sa.eu", "file": "licenses/by-nc-sa.eu.svg", "website": "https://www.creativecommons.org/licenses/by-nc-sa/4.0/"},
			{"name": "cc-by-nc-sa", "file": "licenses/by-nc-sa.svg", "website": "https://www.creativecommons.org/licenses/by-nc-sa/4.0/"},
			{"name": "cc-by-nc.eu", "file": "licenses/by-nc.eu.svg", "website": "https://www.creativecommons.org/licenses/by-nc/4.0/"},
			{"name": "cc-by-nc", "file": "licenses/by-nc.svg", "website": "https://www.creativecommons.org/licenses/by-nc/4.0/"},
			{"name": "cc-by-nd", "file": "licenses/by-nd.svg", "website": "https://www.creativecommons.org/licenses/by-nd/4.0/"},
			{"name": "cc-by-sa", "file": "licenses/by-sa.svg", "website": "https://www.creativecommons.org/licenses/by-sa/4.0/"},
			{"name": "cc-by", "file": "licenses/by.svg", "website": "https://www.creativecommons.org/licenses/by/4.0/"},
			{"name": "cc-zero", "file": "licenses/cc-zero.svg", "website": "https://creativecommons.org/publicdomain/zero/1.0/"}]

def origin_helper(origin, page_size, elem=None, prev_elem=None, prev_elem_origin=None):
	object_origin = [0, 0]
	prev = [0, 0]
	elem_dim = [0, 0]
	#x = lx --> left x
	#pagex - x = rx --> right x
	#y = ty --> top y
	#pagey - y = by --> bottom y

	if ("get_height" in dir(elem)):
		elem_dim[0] = elem.get_height()
		elem_dim[1] = elem.get_width()

	if prev_elem:
		#prev[0], prev[1] = origin_helper(prev_elem_origin, page_size)
		prev[0] = units_to_pixels(prev_elem_origin["rx"], units=origin["units"])
		prev[1] = units_to_pixels(prev_elem_origin["by"], units=origin["units"])

	if ("x" in origin):
		object_origin[0] = units_to_pixels(origin["x"], units=origin["units"])
	elif ("lx" in origin):
		object_origin[0] = units_to_pixels(origin["lx"], units=origin["units"])
	elif ("rx" in origin):
		object_origin[0] = page_size["px"][0] - origin["rx"] - elem_dim[0] - prev[0]
	else:
		object_origin[0] = 0
		print("no x value")

	if ("y" in origin):
		object_origin[1] = units_to_pixels(origin["y"], units=origin["units"])
	elif ("ty" in origin):
		object_origin[1] = units_to_pixels(origin["by"], units=origin["units"])
	elif ("by" in origin):
		object_origin[1] = page_size["px"][1] - origin["by"] - elem_dim[0] - prev[1]
	else:
		print("no y value")
	return object_origin
	
def include_watermark(svg, page_size, prev_elem=None, prev_elem_origin=None):
	watermark_origin =  { "rx": -50, "by": 30, "units": "px" }
	watermark = parse("input/svg/logos/watermark.svg")
	watermark_origin = origin_helper(watermark_origin, page_size, prev_elem=prev_elem, prev_elem_origin=prev_elem_origin)
	watermark_group = G(**kwargs_helper([("id", "watermark"), ("transform", "translate(" + str(watermark_origin[0]) + ", " + str(watermark_origin[1]) + ")")]))
	watermark_group.addElement(watermark)
	print(watermark.get_height())

	svg.addElement(watermark_group)

def include_license(svg, license_data, page_size):
	license_origin = [0, 0]
	licenses_availables = "Availables licenses: "
	license = None
	
	for l in licenses:
		licenses_availables+=(str(l["name"]) + " ")
		if ("name" in license_data):
			if l["name"] == license_data["name"]:
				license = parse(l["file"])
				license_origin = origin_helper(license_data["origin"], page_size)
				license_group = G(**kwargs_helper([("id", "license"), ("transform", "translate(" + str(license_origin[0]) + ", " + str(license_origin[1]) + ")")]))
				license_group.addElement(license)
				svg.addElement(license_group)
				include_watermark(svg, page_size, prev_elem=license, prev_elem_origin=license_data["origin"])
				return
			print("license " + str(license_data["name"]) + " is not supported.")
	print("No license. Consider using one.")
	print(licenses_availables)
	include_watermark(svg, page_size, prev_elem=license)

	return 

from xml.dom import minidom
from xml.dom import Node

def buildx(node_, object):
	attrs = node_.attributes
	if attrs != None:
		setAttributes(attrs, object)
	for child_ in node_.childNodes:
		nodeName_ = child_.nodeName.split(':')[-1]
		if child_.nodeType == Node.ELEMENT_NODE:
			try:
				capitalLetter = nodeName_[0].upper()
				print(capitalLetter+nodeName_[1:])
				objectinstance=eval(capitalLetter+nodeName_[1:]) ()                
			except:
				#print('no class for: ' + nodeName_)
				continue
			object.addElement(buildx(child_,objectinstance))
		elif child_.nodeType == Node.TEXT_NODE:
			#print "TextNode:"+child_.nodeValue
			#if child_.nodeValue.startswith('\n'):
			#    print "TextNode starts with return:"+child_.nodeValue
			#else:
			#print "TextNode is:"+child_.nodeValue
			#object.setTextContent(child_.nodeValue)
			if child_.nodeValue != None and child_.nodeValue.strip() != '':
				# print(len(child_.nodeValue))
				object.appendTextContent(child_.nodeValue)
		elif child_.nodeType == Node.CDATA_SECTION_NODE:  
			object.appendTextContent('<![CDATA['+child_.nodeValue+']]>')          
		elif child_.nodeType == Node.COMMENT_NODE:  
			object.appendTextContent('<!-- '+child_.nodeValue+' -->')          
		else:
			print(child_.nodeType)
			print("Some node:"+nodeName_+" value: "+child_.nodeValue)
	return object

def include_additional(svg, additional_data, page_size):
	for ad in additional_data:
		if (ad["type"] == "svg"):
			external_svg = parse(ad["path"])
			ad_origin = origin_helper(ad["origin"], page_size)
			scale = 1
			if ("scale" in ad):
				scale = ad["scale"]
			
			ad_group = G(**kwargs_helper([("id", ad["name"]), ("transform", "translate(" + str(ad_origin[0]) + ", " + str(ad_origin[1]) + ") scale(" + str(scale) + ")")]))
			if ("mozaic" in ad):
				if (ad["mozaic"] == True):
					print("HEREEEE ",  external_svg.get_width(), " ", external_svg.get_height())
					print(page_size["px"])
					width = int(external_svg.get_width()) * scale
					height = int(external_svg.get_height()) * scale
					ix = 0
					while((ix * width + int(ad_origin[0])) < int(page_size["px"][0])):
						iy = 0
						while((iy * height + int(ad_origin[1])) < int(page_size["px"][1])):
							external_svg_moz = deepcopy(external_svg)
							external_svg_moz.set_x(width * ix + ad_origin[0])
							external_svg_moz.set_y(height * iy + ad_origin[1])
							ad_group.addElement(external_svg_moz)
							iy += 1
						ix += 1
			else:
				ad_group.addElement(external_svg)
			svg.addElement(ad_group)
		if (ad["type"] == "text"):
			tc = [0, 0]
			size = 1 #em
			color = "#000000"
			if "size" in ad:
				print("SIZE")
				size = ad["size"]
				print(size)
			if "center" in ad["origin"]:
				if ad["origin"]["center"] == True:
					em_width = 1 * 6
					tc = text_centerer_helper(size, page_size["px"], ad["text"])
			if "color" in ad:
				color = ad["color"]
			text_origin = origin_helper(ad["origin"], page_size)
			text_group = Text(ad["text"], x=text_origin[0]+tc[0], y=text_origin[1], **kwargs_helper([("style", "font-size:" + str(size) + "em; fill:" + str(color) + ";font-family:Inconsolata;")]))
			svg.addElement(text_group)
		if (ad["type"] == "QRcode"):
			scale = 1
			if ("scale" in ad):
				scale = ad["scale"]
			factory = qrcode.image.svg.SvgImage
			img = qrcode.make(ad["data"], image_factory=factory)
			img.save("temp/qr.svg")
			qrcode_svg = parse("temp/qr.svg")
			qr_origin = origin_helper(ad["origin"], page_size)
			gr_group = G(**kwargs_helper([("transform", "translate(" + str(qr_origin[0]) + ", " + str(qr_origin[1]) + ") scale(" + str(scale) + ")")]))

			qrcode_background = Rect(0, 0, qrcode_svg.get_width(), qrcode_svg.get_height(),  **kwargs_helper([("style", "fill:" + "#ffffff" + ";")]))
			gr_group.addElement(qrcode_background)
			gr_group.addElement(qrcode_svg)
			svg.addElement(gr_group)
		if (ad["type"] == "banner"):
			tc = [0, 0]
			size = 2 #em
			color = "#000000"
			if "size" in ad:
				print("SIZE")
				size = ad["size"]
				print(size)
				# if ad["origin"]["center"] == True:
				# 	em_width = 1 * 6
				# 	tc = text_centerer_helper(size, page_size["px"], ad["text"])
			tc = text_centerer_helper(size, page_size["px"], ad["text"])
			if "color" in ad:
				color = ad["color"]
			text_origin = origin_helper([0,0], page_size)
			banner_height = 30
			banner_background = Rect(0, 0, page_size["px"][0], banner_height, **kwargs_helper([("style", "fill:" + "#00694C" + ";")]))
			banner_text = Text(ad["text"], x=tc[0], y=23, **kwargs_helper([("style", "font-size:" + str(size) + "em; fill:" + str(color) + ";font-family:Inconsolata;")]))
			banner_group = G()
			banner_group.addElement(banner_background)
			banner_group.addElement(banner_text)
			svg.addElement(banner_group)
			pass
			

def include_font_file(font_file, output_file):
	with open(font_file, 'rb') as file:
		ttf_content = file.read()
	
	encoded_tff = base64.b64encode(ttf_content).decode('utf-8')

	header_defs = "<defs>\r\t<style>\r\t\t@font-face {\r\t\t\tfont-family: Inconsolata;\r\t\t\tsrc: url(\"data:application/font-woff;base64,"
	footer_defs = "\")\r\t\t}\r\t</style>\r</defs>"

	for i, line in enumerate(fileinput.FileInput(output_file, inplace=True)):
		if i == 1:
			print(header_defs + encoded_tff + footer_defs)
		print(line, end="")
