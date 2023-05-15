import redis
import subprocess
import xmltodict
import requests
import json
import os
from flask import Flask, request, jsonify

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
prerenderer_url = os.getenv('PRE_URL')
pre_userpassword = os.getenv('PRE_CREDS')
print()


def warmer(url):
    subprocess.run(['wget', '--spider', '--recursive', '--no-directories', '--quiet', url])
    print("url hit: " + url)

def prerender_cache_clearer(url_key):
    redis_client.delete(url_key)
    print("url cache deleted: " + url_key)

def prerender_warmer(url):
    subprocess.run(['curl', '-s', '-o', '/dev/null', '-u', pre_userpassword, prerenderer_url+'/'+url])
    print(pre_userpassword)
    print("url prerender/warmed: " + prerenderer_url+'/'+url)

def cache_warmup_xml_parallel(sitemap_url):
    response = requests.get(sitemap_url, verify=False)
    sitemap_dict = xmltodict.parse(response.content)
    if isinstance(sitemap_dict['urlset']['url'], dict):
        urls = [sitemap_dict['urlset']['url']['loc']]
    else:
        urls = [entry['loc'] for entry in sitemap_dict['urlset']['url']]

    for url in urls:
        warmer(url)
        prerender_cache_clearer(url)
        prerender_warmer(url)
        
    return 'Cache warming complete'

try:
    print(cache_warmup_xml_parallel(os.getenv('SITEMAP_URL')))
except Exception as e:
    print(f"An error occurred while doing the cache warmup: {e}")









