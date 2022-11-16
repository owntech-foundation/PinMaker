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

import helpers
import labels

def legend_title_maker(s, legend_width, legend_title_height, title):

	legend_title_full_rect = Rect(0, 0, legend_width, legend_title_height + 5, rx=int(styles['legend']['cornerRadius']), ry=int(styles['legend']['cornerRadius']))
	legend_title_clip = ClipPath(id="legend_title_rect_id")
	legend_title_clip.addElement(legend_title_full_rect)

	legend_title_rect_arg={}
	legend_title_rect_arg['style'] ='fill:' + styles['legend']['accentColor'] + ' ; stroke-width:0.5; stroke:' + styles['legend']['strokeColor'] + ';'
	legend_title_rect_arg['clip_path'] ='url(#legend_title_rect_id)'

	legend_title_rect = Rect(0, 0, legend_width, legend_title_height, **legend_title_rect_arg)

	legend_title_args={}
	legend_title_args['style'] = 'font-size:1em; font-family:Monospace; fill:' + styles['legend']['titleTextColor']  + '; '
	text_pos = helpers.text_centerer_helper(1, [legend_width, legend_title_height], title)

	legend_title = Text(str(title), text_pos[0], text_pos[1], **legend_title_args)

	s.addElement(legend_title_clip)
	s.addElement(legend_title_rect)
	s.addElement(legend_title)

def legend_maker(svg, styl, omit_styles, omit_categories, legend_data, styles_in_sheets):
	global styles

	styles = styl

	legend_origin = 10, 10 #pixels
	legend_svg = Svg(x=legend_origin[0], y=legend_origin[1])

	legend_inner_spacing = 10
	legend_title_height = 30
	legend_width = 120
	left_offset = 0

	legend_title_svg = Svg()
	legend_title_maker(legend_title_svg, legend_width, legend_title_height, legend_data['title'])

	legend_inner_svg = Svg()

	off = legend_inner_spacing + legend_title_height
	for styl in styles['label']:
		if (("legend" in styles['label'][styl]) and (styles['label'][styl]["legend"] == False)): #do not add special styles
			pass
		elif (styl in omit_styles): #do not add the omited styles
			pass
		elif (styl not in styles_in_sheets):
			pass
		else:
			w = labels.function_label(legend_inner_svg, left_offset, off, "", styles['label'][styl], 0, fwco=4)

			name = styl
			if ("name" in styles['label'][styl]):
				name = styles['label'][styl]['name']
			
			labels.function_label(legend_inner_svg, left_offset + 5 + w, off, name, styles['label']["onlyText"], 0)
			off = off + legend_inner_spacing
	
	if (styles['pwm']['show'] == True):
		legend_inner_svg.addElement(labels.pwm_indicator(left_offset + 3 + 5.92 - 0.08, off + 10))
		labels.function_label(legend_inner_svg, 5 + w, off + helpers.inch_to_pixels(0.04), styles['pwm']['name'], styles['label']["onlyText"], 0)
		off = off + legend_inner_spacing + 3 #This has to do with the origin of the PWM line

	legend_rect_arg={}
	legend_rect_arg['style'] ='fill:' + styles['legend']['fillColor'] +' ; stroke-width:0.5; stroke:' + styles['legend']['strokeColor'] + ';'

	legend_rect = Rect(0, 0, legend_width, off + legend_inner_spacing, rx=int(styles['legend']['cornerRadius']), ry=int(styles['legend']['cornerRadius']), **legend_rect_arg)

	legend_svg.addElement(legend_rect)
	legend_svg.addElement(legend_title_svg)
	legend_svg.addElement(legend_inner_svg)

	svg.addElement(legend_svg)
