import io
import json
import os

import barcode
from barcode.writer import SVGWriter
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg

dirname = os.path.dirname(__file__)
settings_file_path = os.path.join(dirname, 'settings/settings.json')

with open(settings_file_path, 'r') as settings_json_file:
    # Tamanho da página
    page_w, page_h = A4
    settings = json.load(settings_json_file)
    output_path = os.path.join(dirname, 'output', settings['output'])

    rows = settings['grid']['rows']
    cols = settings['grid']['cols']

    # Grid de etiquetas
    margin_x = settings['margin']['x']
    margin_y = settings['margin']['y']

    padding_x = settings['padding']['x']
    padding_y = settings['padding']['y']

    # Tamanho de cada etiqueta
    cell_w = (page_w - 2 * margin_x - (cols - 1) * padding_x) / cols
    cell_h = (page_h - 2 * margin_y - (rows - 1) * padding_y) / rows

    # Inicializa PDF
    c = canvas.Canvas(output_path, pagesize=A4)

    # Classe de código de barras
    code39 = barcode.get_barcode_class('code39')

    # Quantidade total de total_etiquetas
    first_value = settings['range']['first']
    total_codes = settings['range']['qtd']  # ajuste conforme necessário

    for i in range(total_codes):
        valor = str(first_value + i)  # exemplo: códigos de 3000 a 3064

        # Criar código de barras em SVG na memória
        buffer = io.BytesIO()
        barcode_obj = code39(valor, writer=SVGWriter(), add_checksum=False)
        barcode_obj.write(buffer, settings['writer_options'])
        buffer.seek(0)

        # Converter SVG em objeto gráfico
        desenho = svg2rlg(buffer)

        if desenho is None:
            raise ValueError(f"Erro ao converter SVG do código {valor}")

        # Calcular posição na grade
        idx = i
        linha = idx % (rows * cols) // cols
        coluna = idx % cols

        if idx % (rows * cols) == 0 and idx != 0:
            c.showPage()

        # Posição da célula
        x = margin_x + coluna * (cell_w + padding_x)
        y = page_h - margin_y - (linha + 1) * (cell_h + padding_y) + padding_y

        # Escalar o código de barras para caber
        escala_w = cell_w / desenho.width  # NOQA
        escala_h = cell_h / desenho.height
        escala = min(escala_w, escala_h) * 0.95
        desenho.scale(escala, escala)

        # Tamanho final após escala
        largura_codigo = desenho.width * escala
        altura_codigo = desenho.height * escala

        # Centralizar o código na etiqueta
        x_central = x + (cell_w - largura_codigo) / 2
        y_central = y + (cell_h - altura_codigo) / 2

        # Desenhar a borda da etiqueta
        c.setLineWidth(1)
        c.setStrokeColorRGB(0, 0, 0)
        c.rect(x, y, cell_w, cell_h)

        # Desenhar o código centralizado
        renderPDF.draw(desenho, c, x_central, y_central)
    # Finalizar PDF
    c.save()
