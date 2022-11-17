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

import math

import helpers

def function_label_lenght_helper(text, style, added_width, is_italic=True):
	em_size = 3
	margins = 3
	missing_number_offset = 0

	if (("fixed_width_chars" in style) and (style["fixed_width_chars"] > len(text))):
		missing_number_offset = em_size * abs(style["fixed_width_chars"] - len(text)) # width of digit * number of missing digits
	return ((margins * 2) + missing_number_offset + (len(text) * em_size))

def function_label(s, pos_x, pos_y, text, style, added_width, sign=1, is_italic=True, fwco=0):
	#TODO: add auto width
	height = 7.680 #0.08in
	em_size = 3
	skew_angle = 10
	margins = 3
	font_size = "0.5em" #0.42 for linux ?

	kw={}
	kw['style'] = 'font-size:' + font_size + '; font-family:Monospace; fill:' + style["textColor"]  + '; '
	if (is_italic):
		kw['style'] += 'font-style:italic; '

	rect_args={}
	rect_args['style'] ='fill:' + style["fillColor"] + '; stroke-width:0.5; stroke:' + style["strokeColor"] + '; '
	skew_error = 0
	text_margin = 10
	missing_number_offset = 0

	if (style["isSkewed"] == True):
		rect_args['transform'] = 'skewX(-' + str(skew_angle) + ')'
		#get rid of the skew offet by dividing the pos_y to the cot(angle of skew)
		cot = 1 / math.tan(skew_angle * math.pi / 180)
		skew_error = pos_y / cot
		text_margin = 9

	if (fwco != 0):
		missing_number_offset = em_size * abs(fwco - len(text)) #overwrite
	elif (("fixed_width_chars" in style) and (style["fixed_width_chars"] > len(text))):
		missing_number_offset = em_size * abs(style["fixed_width_chars"] - len(text)) # width of digit * number of missing digits


	t = Text(str(text), pos_x + text_margin + margins + (missing_number_offset / 2), pos_y + 7.680 , **kw)
	rwidth = (margins * 2) + missing_number_offset + (len(text) * em_size)
	r = Rect(pos_x + 10 + skew_error, pos_y + 2, rwidth ,  height, 2, 2, **rect_args)

	if ("special" in style):
		if (style["special"] == "hidden"):
			return 0
		elif (style["special"] == "dummy"):
			return rwidth
		elif (style["special"] == "onlyText"):
			s.addElement(t)
			return rwidth

	s.addElement(r)
	s.addElement(t)
	return rwidth

def pwm_indicator(x, y):
	line_style = StyleBuilder()
	line_style.setStrokeWidth(1.92/2) #0.02in
	line_style.setStroke('#212121')
	line_style.setFilling('none')

	pwm_path_origin = 0, 5
	pwm_path = Path('m ' + str(pwm_path_origin[0]) + ' ' + str(pwm_path_origin[1]) + ' c 2 0 2.5 0 3 0 c 1 0 1 -3 3 -3 c 1.5 0 3 3 3 3 c 0 0 1.5 3 3 3 c 2 0 2 -3 3 -3 c 0 0 1 0 3 0', style=line_style.getStyle())
	pwm = Svg(x - pwm_path_origin[0], y - pwm_path_origin[1])
	pwm.addElement(pwm_path)
	return (pwm)

def pin_maker(pin_data, s, x_origin_offset, y_origin_offset, side, styles, omit_styles, omit_categories):
	height = 7.680
	sign = 1

	label_group= G()
	line_group= G()
	line_label_group = G()

	if (side == "L"):
		sign = -1
	
	dot_style = StyleBuilder()
	dot_style.setStrokeWidth(1.92/2) #0.02in
	if (("lineStyle" in pin_data) and ("stroke" in pin_data["lineStyle"])):
		dot_style.setStrokeWidth(pin_data["lineStyle"]["stroke"])

	dot_style.setStroke('#212121')
	dot_style.setFilling('#212121')

	c = Circle(x_origin_offset, (height/2 + 2) + y_origin_offset, 1.92)
	c.set_style(dot_style.getStyle())
	line_group.addElement(c)

	x_offset = 20 #length of the line before the 1st pin indicator
	prev_width = 0
	pr = 10

	for f in pin_data['functions']:
		if (("categories" in f) and helpers.intersection(f["categories"], omit_categories)):
			pass
		elif (("style" in f) and f["style"] in omit_styles):
			pass
		else:
			lenght_label = 0
			error_offset = 0

			if (side == "L"):
				lenght_label = function_label_lenght_helper(f['name'], styles['label'][f['style']], 0)
				error_offset = 17.941 #surely due to the skew thinggy

			pr = function_label(label_group, sign * (x_offset + prev_width + lenght_label + error_offset) + x_origin_offset, y_origin_offset, f['name'], styles['label'][f['style']], 0, sign)

			if (pr != 0): #for the hidden tag
				prev_width = prev_width + pr + 3

	pwm_offeset = 0
	pwm_overlap = 0 #to ensure there is no gap between the line and pwm sign (only when pwmsign is needed)

	if (("isPWM" in pin_data) and (pin_data["isPWM"] == True)):
		
		pwmLength = 0
		if (side == "L"):
			pwmLength = 18 #lenght of the path

		line_group.addElement(pwm_indicator(x_origin_offset + sign * (pwmLength + 5), y_origin_offset + 5.92 - 0.08))

		pwm_offeset = 18 + 5
		pwm_overlap = 0.1

		small_line = Line(x_origin_offset, (height/2 + 2) + y_origin_offset, x_origin_offset + (sign * (5 + pwm_overlap)), (height/2 + 2) + y_origin_offset)
		small_line.set_style(dot_style.getStyle())
		line_group.addElement(small_line)

	big_line = Line(x_origin_offset + (sign * (pwm_offeset - pwm_overlap)), (height/2 + 2) + y_origin_offset, (sign * (prev_width + x_offset)) + x_origin_offset, (height/2 + 2) + y_origin_offset)
	big_line.set_style(dot_style.getStyle())

	line_group.addElement(big_line)
	line_label_group.addElement(line_group)
	line_label_group.addElement(label_group)
	s.addElement(line_label_group)
