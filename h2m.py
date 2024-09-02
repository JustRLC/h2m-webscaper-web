import subprocess
import sys

def install_packages():
    try:
        import requests
    except ImportError:
        print("requests module not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    try:
        import bs4
    except ImportError:
        print("beautifulsoup4 module not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
    try:
        import flask
    except ImportError:
        print("flask module not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])

install_packages()


from flask import Flask, jsonify, send_file, render_template
import json
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape')
def scrape_data():
    url = 'https://master.iw4.zip/servers'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    h2m_panel = soup.find('div', id='H2M_servers')
    server_rows = h2m_panel.find_all('tr', class_='server-row')

    # This is where you extract data. This is an example.
    #data = {
    #    "title": soup.title.string,
    #    "links": [a['href'] for a in soup.find_all('a', href=True)]
    #}

    ip_port_list = []
    for row in server_rows:
        ip = row['data-ip']
        port = row['data-port']
        ip_port_list.append(f"{ip}:{port}")

    favourites_file = 'favourites.json'
    try:
        with open(favourites_file, 'r') as file:
            try:
                favourites = json.load(file)
            except json.JSONDecodeError:
                favourites = []
    except FileNotFoundError:
        favourites = []

    favourites.extend(ip_port_list)
    favourites = list(set(favourites))
    
    # Save data to a JSON file
    with open(favourites_file, 'w') as file:
        json.dump(favourites, file, indent=4)
    
    return jsonify({"file_url": f"/download/{favourites_file}"})

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)


@app.route('/check_status')
def check_status():
    url = 'https://master.iw4.zip/'
    try:
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            return jsonify({"status": "up"})
        else:
            return jsonify({"status": "down"})
    except requests.RequestException:
        return jsonify({"status": "down"})

if __name__ == '__main__':
    app.run(debug=True, host="10.8.81.10", port=8080)
