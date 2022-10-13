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

import argparse

#png viewer
import cairosvg
from PIL import Image

def show_svg(file_path, width, height):
	cairosvg.svg2png(url=file_path, write_to=file_path + ".png", output_width=width, output_height=height)
	i = Image.open(file_path + ".png")
	i.show()

def function_label_lenght_helper(text, style, added_width, is_italic=True):
    em_size = 3
    margins = 3
    missing_number_offset = 0

    if (("fixed_width_chars" in style) and (style["fixed_width_chars"] > len(text))):
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

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

def pin_maker(pin_data, s, x_origin_offset, y_origin_offset, side):
    height = 7.680
    sign = 1
    if (side == "L"):
        sign = -1
    
    dot_style = StyleBuilder()
    dot_style.setStrokeWidth(1.92/2) #0.02in
    if (("lineStyle" in pin_data) and ("stroke" in pin_data["lineStyle"])):
        dot_style.setStrokeWidth(pin_data["lineStyle"]["stroke"]) #0.02in

    dot_style.setStroke('#212121')
    dot_style.setFilling('#212121')

    c = Circle(x_origin_offset, (height/2 + 2) + y_origin_offset, 1.92)
    c.set_style(dot_style.getStyle())
    s.addElement(c)

    x_offset = 20 #length of the line before the 1st pin indicator
    prev_width = 0
    pr = 10

    pinsvg = Svg()

    for f in pin_data['functions']:
        if (("categories" in f) and intersection(f["categories"], omit_categories)):
            pass
        elif (("style" in f) and f["style"] in omit_styles):
            pass
        else:
            lenght_label = 0
            error_offset = 0

            if (side == "L"):
                lenght_label = function_label_lenght_helper(f['name'], styles[f['style']], 0)
                error_offset = 17.941 #surely due to the skew thinggy

            pr = function_label(pinsvg, sign * (x_offset + prev_width + lenght_label + error_offset) + x_origin_offset, y_origin_offset, f['name'], styles[f['style']], 0, sign)

            if (pr != 0): #for the hidden tag
                prev_width = prev_width + pr + 3

    pwm_offeset = 0

    if (("isPWM" in pin_data) and (pin_data["isPWM"] == True)):
        
        pwmLength = 0
        if (side == "L"):
            pwmLength = 18 #lenght of the path

        s.addElement(pwm_indicator(x_origin_offset + sign * (pwmLength + 5), y_origin_offset + 5.92 - 0.08))

        pwm_offeset = 18 + 5

        small_line = Line(x_origin_offset, (height/2 + 2) + y_origin_offset, x_origin_offset + sign * 5, (height/2 + 2) + y_origin_offset)
        small_line.set_style(dot_style.getStyle())
        s.addElement(small_line)

    big_line = Line(x_origin_offset + (sign * pwm_offeset), (height/2 + 2) + y_origin_offset, (sign * (prev_width + x_offset)) + x_origin_offset, (height/2 + 2) + y_origin_offset)
    big_line.set_style(dot_style.getStyle())
    s.addElement(big_line)

    s.addElement(pinsvg)

def legend_maker(s):
    legend_origin = 10, 10 #pixels
    legend_svg = Svg(x=legend_origin[0], y=legend_origin[1])# "legend")

    legend_rect_arg={}
    legend_rect_arg['style'] ='fill:#f1f1f1 ; stroke-width:0.5; stroke:#d1d1d1; '
    
    rect = Rect(0, 0, 110, 200, rx=5, ry=5, **legend_rect_arg)
    #TODO: auto resize the legend
    legend_svg.addElement(rect)

    off = 10
    for styl in styles:
        if (("legend" in styles[styl]) and (styles[styl]["legend"] == False)): #do not add special styles
            pass
        elif (styl in omit_styles): #do not add the omited styles
            pass
        elif 0: #TODO: omit the non present styles of the file
            pass
        else:
            w = function_label(legend_svg, 10, off, "    ", styles[styl], 0)

            name = styl
            if ("name" in styles[styl]):
                name = styles[styl]['name']
            
            function_label(legend_svg, 10 + w, off, name, styles["onlyText"], 0)
            off = off + 10
    
    #s.addElement(pwm_indicator(x_origin_offset + sign * (pwmLength + 5), y_origin_offset + 5.92 - 0.08))
    legend_svg.addElement(pwm_indicator(13 + 5.92 - 0.08, off + 10))
    function_label(legend_svg, 23 + 5.92 - 0.08, off + 4, "HRTIM PWM", styles["onlyText"], 0)
    print(legend_svg.get_height())

    s.addElement(legend_svg)

def customSort(k):
    return (style_order.index(k['style']))

def style_order_helper():
    global style_order

    style_order = []
    for styl in styles:
        style_order.append(styl)

def order_chooser(elems, order):
    if (order == "regular"):
        return(elems)
    elif (order == "reversed"):
        return(reversed(elems))
    else:
        raise Exception("order needs to be 'regular' or 'reversed'")

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

def load_pins_file(filepath, svg):
    style_order_helper()
    f = open(filepath)
    board_data = json.load(f)

    for group in board_data:
        units = "px"
        if ("units" in group["origin"]):
            units = group["origin"]["units"]
        
        x = units_to_pixels(group["origin"]["x"], units)
        y = units_to_pixels(group["origin"]["y"], units)

        order="regular"
        if ("order" in group):
            order = group["order"]

        for pind in group["pins"]:
            pin_functions = pind["functions"]
            pin_functions.sort(key=customSort) #sort the label within pin with the order of the styles in the style.json

        for b in order_chooser(group["pins"], order):
            pin_maker(b, svg, x, y, group["side"])

            spacing = inch_to_pixels(0.1)
            if ("spacing" in group):
                spacing = group["spacing"]
                
            y = y + mm_to_pixels(spacing)
    f.close()

if __name__ == '__main__': 
    global styles
    global omit_categories
    global sheet_name

    s = Svg(0, 0, mm_to_pixels(297), mm_to_pixels(210)) #TODO: auto choose the size of the canvas
    # A4 paper = 210 x 297 mm


    
    all_args = argparse.ArgumentParser()

    all_args.add_argument('-p', "--pins", action='append', required=True, help="pins.json file(s)")
    all_args.add_argument("-s", "--style", required=False, help="style.json file")
    all_args.add_argument('-os', "--omit_styles", action='append', required=False, help="prevent plotting of a style")
    all_args.add_argument('-oc', "--omit_categories", action='append', required=False, help="prevent plotting of a category")
    all_args.add_argument("-l", "--legend", action='store_true', required=False, help="plotting the legend")
    all_args.add_argument("-o", "--output", required=False, help="name of the output file (pinout.svg is the default value)")
    all_args.add_argument("-n", "--name", required=False, help="name of the sheet.")

    args = vars(all_args.parse_args())
    print(args)
    style_file = 'styles.json'
    if (args['style']):
        style_file = args['style']

    fstyles = open(style_file)
    styles = json.load(fstyles)
    fstyles.close()

    omit_categories = []
    omit_styles = []

    omit_categories = []#["extended"] #["alternate", "additional"]
    omit_styles = [] #["timer", "audio", "usb", "rtc", "analog"] #["timer"]

    # omit_styles = ["portPin", "default", "led", "timer", "adc", "dac", "i2c", "spi", "audio", "control", "jtag", "usb", "rtc"] #["timer"]


    if (args['legend']):
        legend_maker(s)

    output_file = "pinout.svg"
    if (args['output']):
        output_file = str(args['output'])

    sheet_name = "LEGEND"
    if (args['name']):
        sheet_name = str(args['name'])

    for pin_file in args['pins']:
        load_pins_file(pin_file, s)

    s.save(output_file)
    show_svg(output_file, s.get_width(), s.get_height())