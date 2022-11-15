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
import os
from termcolor import colored, cprint

import helpers
import png_renderer

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

            pr = function_label(pinsvg, sign * (x_offset + prev_width + lenght_label + error_offset) + x_origin_offset, y_origin_offset, f['name'], styles['label'][f['style']], 0, sign)

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

def text_centerer_helper(em, elem, text):
    #1em = 0.08in height
    #1em = 6px char width
    em_width = em * 6
    em_height = em * helpers.inch_to_pixels(0.08)
    x = (elem[0] / 2) - ((len(text) * em_width) / 2)
    y = (elem[1] / 2) + (em_height / 2)

    return (x, y)

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
    text_pos = text_centerer_helper(1, [legend_width, legend_title_height], title)

    legend_title = Text(str(title), text_pos[0], text_pos[1], **legend_title_args)

    s.addElement(legend_title_clip)
    s.addElement(legend_title_rect)
    s.addElement(legend_title)

def legend_maker(s):
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
            w = function_label(legend_inner_svg, left_offset, off, "", styles['label'][styl], 0, fwco=4)

            name = styl
            if ("name" in styles['label'][styl]):
                name = styles['label'][styl]['name']
            
            function_label(legend_inner_svg, left_offset + 5 + w, off, name, styles['label']["onlyText"], 0)
            off = off + legend_inner_spacing
    
    if (styles['pwm']['show'] == True):
        legend_inner_svg.addElement(pwm_indicator(left_offset + 3 + 5.92 - 0.08, off + 10))
        function_label(legend_inner_svg, 5 + w, off + helpers.inch_to_pixels(0.04), styles['pwm']['name'], styles['label']["onlyText"], 0)
        off = off + legend_inner_spacing + 3 #This has to do with the origin of the PWM line

    legend_rect_arg={}
    legend_rect_arg['style'] ='fill:' + styles['legend']['fillColor'] +' ; stroke-width:0.5; stroke:' + styles['legend']['strokeColor'] + ';'

    legend_rect = Rect(0, 0, legend_width, off + legend_inner_spacing, rx=int(styles['legend']['cornerRadius']), ry=int(styles['legend']['cornerRadius']), **legend_rect_arg)

    legend_svg.addElement(legend_rect)
    legend_svg.addElement(legend_title_svg)
    legend_svg.addElement(legend_inner_svg)

    s.addElement(legend_svg)

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

def load_pins_file(filepath, svg):
    f = open(filepath)
    board_data = json.load(f)
    f.close()

    global legend_data
    legend_data = board_data["legend"]
    
    for group in board_data["groups"]:
        units = "px"
        if ("units" in group["origin"]):
            units = group["origin"]["units"]
        
        x = helpers.units_to_pixels(group["origin"]["x"], units)
        y = helpers.units_to_pixels(group["origin"]["y"], units)
        
        #adding all the syles encountered in a list for the legend
        for pind in group["pins"]:
            for func in pind["functions"]:
                if func["style"] not in styles_in_sheets:
                    styles_in_sheets.append(func["style"]) 

        #choosing the order (from top to bottom aka regular or from bottom to top aka reversed)
        order="regular"
        if ("order" in group):
            order = group["order"]

        #sort the pins with their style
        for pind in group["pins"]:
            pin_functions = pind["functions"]
            pin_functions.sort(key=style_sort) #sort the label within pin with the order of the styles in the style.json

        #make the pin
        for b in order_chooser(group["pins"], order):
            pin_maker(b, svg, x, y, group["side"])

            spacing = helpers.inch_to_pixels(0.1)
            if ("spacing" in group):
                spacing = group["spacing"]
                
            y = y + helpers.mm_to_pixels(spacing)

# def categories_helper(filepath_array):
#     for (filepath in filepath_array):
#         f = open(filepath)
#         board_data = json.load(f)
#         f.close()
#         for group in board_data["groups"]:
#             for f in pin_data['functions']:


if __name__ == '__main__': 
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

    if (args['omit_styles']):
        for omit_styles_arg in args['omit_styles']:
            if (omit_styles_arg not in styles['label']):
                cprint("Warning: '" + omit_styles_arg + "' is not present in the style file. skipping", "yellow")

            else:
                omit_styles.append(omit_styles_arg)

    if (args['omit_categories']):
        for omit_categories_arg in args['omit_categories']:
            omit_categories.append(omit_categories_arg)

    style_order_helper()
    for pin_file in args['pins']:
        load_pins_file(pin_file, s)

    if (args['legend']):
        legend_maker(s)

    output_file = "pinout.svg"
    if (args['output']):
        output_file = str(args['output'])

    s.save(output_file)
    if (args['show']):
        png_renderer.show_svg(output_file, s.get_width(), s.get_height())

    if (args['inkscape']):
        if (helpers.is_tool("inkscape")):
            os.system("inkscape " + output_file + " &")
        else:
            helpers.inkscape_not_here_helper()
