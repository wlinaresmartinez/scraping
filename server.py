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
