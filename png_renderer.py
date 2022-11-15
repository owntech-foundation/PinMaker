from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from PIL import Image

def show_svg(file_path, width, height):
    drawing = svg2rlg(file_path)
    scale = 3
    drawing.scale(scale, scale)
    renderPM.drawToFile(d=drawing, fn=file_path + ".png", fmt="PNG", dpi=72 * scale)
    
    i = Image.open(file_path + ".png")
    i.show()
