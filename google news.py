from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import threading
import time

app = Flask(__name__)

progress = {'finished': 0, 'total': 0}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_download')
def start_download():
    query = request.args.get('query')
    thread = threading.Thread(target=download_pages, args=(query,))
    thread.start()
    return jsonify({'status': 'started'})

@app.route('/progress')
def get_progress():
    return jsonify(progress)

def download_pages(query):
    url = f'https://news.google.com/search?q={query}&hl=it&gl=IT&ceid=IT:it'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    elements = soup.find_all(class_='IFHyqb DeXSAc')
    
    progress['total'] = len(elements)
    progress['finished'] = 0

    if len(elements) == 0:
        progress['total'] = 1  # Set total to 1 to prevent division by zero
        return

    output_file_path = r'C:\Users\fabio\OneDrive\Desktop\googlenews search1\googlenews_search1.txt'
    base_url = 'https://news.google.com'

    with open(output_file_path, 'w', encoding='utf-8') as file:
        for idx, element in enumerate(elements):
            link = element.find('a', href=True)
            if link:
                href = link['href']
                full_url = base_url + href[1:]
                try:
                    page_response = requests.get(full_url)
                    page_response.raise_for_status()  # Raise an HTTPError for bad responses
                    page_soup = BeautifulSoup(page_response.content, 'html.parser')
                    page_text = page_soup.get_text(separator=' ', strip=True)
                    
                    file.write(f"Element {idx + 1}\n")
                    file.write(f"URL: {full_url}\n")
                    file.write(f"Content:\n{page_text}\n")
                    file.write("----------\n")
                except requests.exceptions.RequestException as e:
                    file.write(f"Element {idx + 1}\n")
                    file.write(f"URL: {full_url}\n")
                    file.write("Error: Could not retrieve content\n")
                    file.write("----------\n")
                
                progress['finished'] += 1
                if progress['finished'] >= progress['total']:
                    break
                time.sleep(1)  # Simulate a delay for demonstration purposes

if __name__ == '__main__':
    app.run(debug=True)
