import subprocess
import json
import concurrent.futures
import xmltodict
from datetime import timedelta
import requests
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import os

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_TOKEN')
jwt = JWTManager(app)

USERNAME = os.getenv('CRAWLER_USERNAME')
PASSWORD = os.getenv('CRAWLER_PASSWORD')

# JWT token generation
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    expire = request.json.get('expire_secs')
    if USERNAME !=username or PASSWORD !=password:
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity=username, expires_delta=timedelta(seconds=int(expire)))
    return jsonify(access_token=access_token), 200

@app.route('/cache_warmup', methods=['POST'])
@jwt_required()
def cache_warmup():
    data = json.loads(request.data)
    urls = data['urls']
    print('test')
    print(urls)
    for url in urls:
        subprocess.run(['wget', '--spider', '--recursive', '--no-directories', '--quiet', url])
        print("url hit")
    return 'Cache warming complete'


@app.route('/cache_warmup_xml', methods=['POST'])
@jwt_required()  
def cache_warmup_xml():
    sitemap_url = request.json['sitemap_url']
    response = requests.get(sitemap_url)
    sitemap_dict = xmltodict.parse(response.content)
    urls = [entry['loc'] for entry in sitemap_dict['urlset']['url']]
    for url in urls:
        subprocess.run(['wget', '--spider', '--recursive', '--no-directories', '--quiet', url])
        print("url hit")
    return 'Cache warming complete'

@app.route('/cache_warmup_xml_parallel', methods=['POST'])
@jwt_required()
def cache_warmup_xml_parallel():
    sitemap_url = request.json['sitemap_url']
    response = requests.get(sitemap_url)
    sitemap_dict = xmltodict.parse(response.content)
    urls = [entry['loc'] for entry in sitemap_dict['urlset']['url']]
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for url in urls:
            futures.append(executor.submit(wget, url))
        
        # Wait for all futures to complete
        concurrent.futures.wait(futures)
        
    return 'Cache warming complete'

def wget(url):
    subprocess.run(['wget', '--spider', '--recursive', '--no-directories', '--quiet', url])
    print("url hit:", url)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)