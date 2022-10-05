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
import math

#png viewer
import cairosvg
from PIL import Image

def show_svg(svg_data):
	cairosvg.svg2png(url=svg_data, write_to='testoutput/test.png', output_width=1000, output_height=1000)
	i = Image.open('testoutput/test.png')
	i.show()

def pin_number(s, pos_x, pos_y, text, style, added_width, is_italic=True):
	#todo: add auto width
	height = 7.680 #0.08in
	em_size = 3
	skew_angle = 10
	margins = 3
	kw={}
	kw['style'] = 'font-size:0.5em; font-family:Monospace; fill:' + style["textColor"]  + '; '
	if (is_italic):
		kw['style'] += 'font-style:italic; '

	rect_args={}
	rect_args['style'] ='fill:' + style["fillColor"] + '; stroke-width:0.5; stroke:' + style["strokeColor"] + '; '
	skew_error = 0
	text_margin = 10
	if (style["isSkewed"] == True):
		rect_args['transform'] = 'skewX(-' + str(skew_angle) + ')'
		#get rid of the squew offet by dividing the pos_y to the cot(angle of squew)
		skew_error = (pos_y / (1 / math.tan(skew_angle * math.pi / 180))) 
		text_margin = 9

	t = Text(str(text), pos_x + text_margin + margins, pos_y + 7.680 , **kw)
	rwidth = margins + (len(text) * em_size) + margins
	r = Rect(pos_x + 10 + skew_error, pos_y + 2, rwidth ,  height, 2, 2, **rect_args)

	if (style["fillColor"] != "#ffffff00"): #dummy
		s.addElement(r)
		s.addElement(t)
	return rwidth

def pin_maker(pin_data, s, y_offset):
	height = 7.680

	line_style = StyleBuilder()
	#line_style.setStrokeWidth(1.92) #0.02in
	line_style.setStroke('#212121')
	line_style.setFilling('#212121')

	c = Circle(1.92*2, (height/2 + 2) + y_offset, 1.92)
	c.set_style(line_style.getStyle())
	s.addElement(c)

	x_offset = 20
	prev_width = 0
	pr = 10

	pinsvg = Svg()

	for f in pin_data['functions']:
		pr = pin_number(pinsvg, 0 + x_offset + prev_width, y_offset, f['name'], styles[f['style']], 0)
		prev_width = prev_width + pr + 3

	l = Line(1.92, (height/2 + 2) + y_offset, prev_width + x_offset, (height/2 + 2) + y_offset)
	l.set_style(line_style.getStyle())
	s.addElement(l)
	s.addElement(pinsvg)

if __name__ == '__main__': 
    #tutorialChain()
    #load_tutorial()
    global styles

    s = Svg(0, 0, 500, 500)
    
    # Opening JSON file
    fstyles = open('styles.json')
    styles = json.load(fstyles)
    fstyles.close()

    f = open('spin_pins.json')
    board_data = json.load(f)
    y_offset = 50
    for b in board_data:
        pin_maker(b, s, y_offset)
        y_offset = y_offset + 9.6 #0.1in
    f.close()
    
    s.save('./testoutput/pinout.svg')
    show_svg('testoutput/pinout.svg')