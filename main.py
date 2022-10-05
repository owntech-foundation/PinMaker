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

def function_label_lenght_helper(text, style, added_width, is_italic=True):
    em_size = 3
    margins = 3
    missing_number_offset = 0
    if ("fixed_width_chars" in style):
        if (style["fixed_width_chars"] > len(text)):
            missing_number_offset = em_size * abs(style["fixed_width_chars"] - len(text)) # width of digit * number of missing digits
    return ((margins * 2) + missing_number_offset + (len(text) * em_size))

def function_label(s, pos_x, pos_y, text, style, added_width, sign=1, is_italic=True):
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
    missing_number_offset = 0

    if (style["isSkewed"] == True):
        rect_args['transform'] = 'skewX(-' + str(skew_angle) + ')'
        #get rid of the skew offet by dividing the pos_y to the cot(angle of skew)
        cot = 1 / math.tan(skew_angle * math.pi / 180)
        skew_error = pos_y / cot
        text_margin = 9

    if ("fixed_width_chars" in style):
        if (style["fixed_width_chars"] > len(text)):
            missing_number_offset = em_size * abs(style["fixed_width_chars"] - len(text)) # width of digit * number of missing digits
    t = Text(str(text), pos_x + text_margin + margins + (missing_number_offset / 2), pos_y + 7.680 , **kw)
    rwidth = (margins * 2) + missing_number_offset + (len(text) * em_size)
    r = Rect(pos_x + 10 + skew_error, pos_y + 2, rwidth ,  height, 2, 2, **rect_args)

    if (style["fillColor"] != "#ffffff00"): #dummy
        s.addElement(r)
        s.addElement(t)
    return rwidth

def pin_maker(pin_data, s, x_origin_offset, y_origin_offset):
    height = 7.680
    sign = 1
    if (pin_data["side"] == "L"):
        sign = -1
    line_style = StyleBuilder()
    #line_style.setStrokeWidth(1.92) #0.02in
    line_style.setStroke('#212121')
    line_style.setFilling('#212121')

    c = Circle(x_origin_offset, (height/2 + 2) + y_origin_offset, 1.92)
    c.set_style(line_style.getStyle())
    s.addElement(c)

    x_offset = 20 #length of the line before the 1st pin indicator
    prev_width = 0
    pr = 10

    pinsvg = Svg()

    for f in pin_data['functions']:

        lenght_label = 0
        error_offset = 0
        if (pin_data["side"] == "L"):
            lenght_label = function_label_lenght_helper(f['name'], styles[f['style']], 0)
            error_offset = 17.941 #surely due to the skew thinggy

        pr = function_label(pinsvg, sign * (x_offset + prev_width + lenght_label + error_offset) + x_origin_offset, y_origin_offset, f['name'], styles[f['style']], 0, sign)

        prev_width = prev_width + pr + 3

    l = Line(x_origin_offset, (height/2 + 2) + y_origin_offset, (sign * (prev_width + x_offset)) + x_origin_offset, (height/2 + 2) + y_origin_offset)
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

    y_origin_offset = 50
    x_origin_offset = 200
    fl = open('spin_pins_L.json')
    board_data = json.load(fl)
    for b in board_data:
        pin_maker(b, s, x_origin_offset, y_origin_offset)
        y_origin_offset = y_origin_offset + 9.6 #0.1in
    fl.close()

    y_origin_offset = 50
    x_origin_offset = 250

    fr = open('spin_pins_R.json')
    board_data = json.load(fr)
    for b in board_data:
        pin_maker(b, s, x_origin_offset, y_origin_offset)
        y_origin_offset = y_origin_offset + 9.6 #0.1in
    fr.close()

    y_origin_offset = 300
    x_origin_offset = 250

    fb = open('spin_pins_B.json')
    board_data = json.load(fb)
    for b in board_data:
        pin_maker(b, s, x_origin_offset, y_origin_offset)
        y_origin_offset = y_origin_offset + 9.6 #0.1in
    fb.close()

    s.save('./testoutput/pinout.svg')
    show_svg('testoutput/pinout.svg')