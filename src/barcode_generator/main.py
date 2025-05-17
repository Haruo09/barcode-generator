import json
from pprint import pprint
from io import BytesIO

import barcode
from barcode.writer import SVGWriter
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

with open('./settings/settings.json', 'r') as settings_json:
    settings = json.load(settings_json)
    page_width, page_height = A4

    cell_width = (
        page_width
        - 2 * settings['margin']['x']
        - (settings['grid']['cols'] - 1) * settings['padding']['x']
    ) / settings['grid']['cols']
    cell_height = (
        page_height
        - 2 * settings['margin']['y']
        - (settings['grid']['rows'] - 1) * settings['padding']['y']
    ) / settings['grid']['rows']

    pdf = canvas.Canvas(settings['output'], pagesize=A4)

    class_code = barcode.get_barcode_class(settings['code-class'])
    
    for index in range(settings['range']['first'], settings['range']['first'] + settings['range']['qtd']):
        value = str(index)

        buffer = BytesIO()
        barcode_obj = class_code(value, writer=SVGWriter, add_checksum=False)
        barcode_obj.write(buffer, {
            "module_width": settings["writer_options"]["module_width"],
            "module_height": settings["writer_options"]["module_height"],
            "font_size": settings["writer_options"]["font_size"]
        })
        buffer.seek(0)

    print('Tudo certo')
