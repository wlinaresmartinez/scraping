# # LECTOR DE LINKS DSDE ARCHIVO .TXT Y EXPORTA EN HTML TODOS LOS LINKS

# import requests

# def scrape_html(url):
#     response = requests.get(url)
#     if response.status_code == 200:
#         return response.text
#     else:
#         return None

# def read_links_from_file(file_path):
#     with open(file_path, 'r', encoding='utf-8') as file:
#         links = file.readlines()
#     return [link.strip() for link in links]

# def main():
#     file_path = 'links.txt'
#     output_file = 'codigo.html'

#     links = read_links_from_file(file_path)

#     html = ''
#     for link in links:
#         scraped_html = scrape_html(link)
#         if scraped_html:
#             html += scraped_html

#     with open(output_file, 'w', encoding='utf-8') as file:
#         file.write(html)

# if __name__ == '__main__':
#     main()


# SCRIPT PARA LEER LOS DATOS DE ARCHIVOS HTML Y EXPORTA EN  JSON


# import json
# from bs4 import BeautifulSoup

# # Abrir el archivo HTML
# with open("codigo.html", "r", encoding="utf8") as file:
#     # Leer el contenido del archivo
#     html_content = file.read()

# # Crear el objeto BeautifulSoup
# soup = BeautifulSoup(html_content, "html.parser")

# # Buscar los tags "td" y "tr" con las clases especificadas
# td_tags = soup.find_all("td", class_=["texto12", "texto_18", "texto10","medicina"])
# # tr_tags = soup.find_all("tr", class_="medicina")

# # Listas para almacenar el resultado
# resultado = []

# # Función para eliminar los caracteres "\n" y "\t" del texto
# def eliminar_caracteres_especiales(texto):
#     texto = texto.replace("\n", "").replace("\t", "")
#     return texto

# # Obtener el texto de los tags "td" encontrados
# for td_tag in td_tags:
#     texto = eliminar_caracteres_especiales(td_tag.text)
#     resultado.append(texto)

# # Obtener el texto de los tags "tr" encontrados
# # for tr_tag in tr_tags:
# #     texto = eliminar_caracteres_especiales(tr_tag.text)
# #     resultado.append(texto)

# # Exportar el resultado a un archivo JSON
# with open("resultado.json", "w", encoding="utf8") as outfile:
#     json.dump(resultado, outfile, ensure_ascii=False, indent=4)


# Script para dividir los datos en el json

# import pandas as pd

# # Leer el archivo .json
# data = pd.read_json("resultado.json")

# # Convertir los datos a formato .json
# data_json = data.to_json(orient="records")

# # Guardar los datos en un nuevo archivo .json
# with open("nuevo_archivo.json", "w") as outfile:
#     outfile.write(data_json)


# from flask import Flask, request, render_template, send_file
# import requests
# from bs4 import BeautifulSoup
# import json
# import unidecode

# app = Flask(__name__)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         # Procesar el archivo .txt y generar el archivo .html
#         file = request.files['txt_file']
#         links = file.read().decode().splitlines()
#         html_content = ""
        
#         for link in links:
#             response = requests.get(link)
#             soup = BeautifulSoup(response.text, 'html.parser')
#             html_content += soup.prettify()

#         # Convertir los caracteres a su forma ASCII
#         html_content = unidecode.unidecode(html_content)
        
#         with open('pagina.html', 'w', encoding='utf-8') as output_file:
#             output_file.write(html_content)
        
#         return render_template('index.html', html_file=True)
    
#     return render_template('index.html')

# @app.route('/download-html')
# def download_html():
#     return send_file('pagina.html', as_attachment=True)

# @app.route('/process-json', methods=['POST'])
# def process_json():
#     # Leer el archivo .html
#     with open('pagina.html', 'r', encoding='utf-8') as file:
#         html_content = file.read()

#     # Convertir los caracteres a su forma ASCII
#     html_content = unidecode.unidecode(html_content)

#     # Analizar el contenido HTML
#     soup = BeautifulSoup(html_content, 'html.parser')

#     # Buscar los tag "td" con las clases especificadas y extraer los textos
#     # Convertir los textos a su forma ASCII
#     texts = [unidecode.unidecode(td.text) for td in soup.find_all('td', class_=['texto10', 'texto18', 'texto_18', 'medicina'])]

#     # Guardar los textos en un archivo .json
#     with open('resultados.json', 'w', encoding='utf-8') as file:
#         json.dump(texts, file, ensure_ascii=False)
        
#     return send_file('resultados.json', as_attachment=True)

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, jsonify, make_response
import requests
from bs4 import BeautifulSoup
import json
import csv
import io

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename.endswith('.txt'):
            links = [line.strip() for line in file]
            texts = scrape_links(links)
            return render_template('index.html', texts=texts)
    return render_template('index.html')

@app.route('/export', methods=['POST'])
def export():
    texts = request.form.getlist('texts[]')
    format = request.form.get('format')
    
    if format == 'json':
        data = {'texts': texts}
        json_data = json.dumps(data, indent=4, ensure_ascii=False)
        response = make_response(json_data)
        response.headers['Content-Disposition'] = 'attachment; filename=export.json'
        response.headers['Content-Type'] = 'application/json'
        return response
    
    if format == 'txt':
        text_data = '\n'.join(texts)
        response = make_response(text_data)
        response.headers['Content-Disposition'] = 'attachment; filename=export.txt'
        response.headers['Content-Type'] = 'text/plain'
        return response
    
    if format == 'csv':
        csv_data = [['text']]
        csv_data.extend([[text] for text in texts])
        csvfile = io.StringIO()
        writer = csv.writer(csvfile)
        writer.writerows(csv_data)
        csvfile.seek(0)
        response = make_response(csvfile.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=export.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response

def scrape_links(links):
    texts = []
    for link in links:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # for tag in soup.find_all('td', class_=['texto10', 'texto18', 'texto_18', 'texto12']):
        #     texts.append(tag.text.strip())
        
        for tag in soup.find_all('td', attrs={'colspan': '4'}):
            texts.append(tag.text.strip())

        for tag in soup.find_all('td', attrs={'colspan': '1'}):
            texts.append(tag.text.strip())

        for tag in soup.find_all('td', attrs={'colspan': '2'}):
            texts.append(tag.text.strip())
    
    return texts

if __name__ == '__main__':
    app.run()
