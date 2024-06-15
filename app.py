import json
from dotenv import load_dotenv
import streamlit as st
import os 
import requests
from config import OpenAIConfig
from playwright.async_api import async_playwright
import google.generativeai as genai
from PIL import Image
import io
from fake_useragent import UserAgent
import tiktoken
from playwright.sync_api import sync_playwright, Playwright
from prompts import prompts
from urllib.parse import urlparse
import re

# logging.basicConfig(
#     format="%(levelname)s [%(asctime)s] %(name)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
#     level=logging.DEBUG
# )

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def get_image(playwright: Playwright, url):
    chromium = playwright.chromium
    browser = chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url)
    img = page.screenshot(full_page=True)
    img = Image.open(io.BytesIO(img))
    browser.close()
    return img

def dynamic_response(url,headless=False):
    with sync_playwright() as playwright:
        chromium = playwright.chromium 
        browser = chromium.launch(headless=headless)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(3000)
        html = page.content()
        browser.close()
        return html

def gemini_response(response, prompt):
    model = genai.GenerativeModel('gemini-1.5-pro')
    print('getting response...')
    response = model.generate_content([f'{prompt}\n',response])
    return response.candidates[0].content.parts[0].text

def html_scraper(url):
    req = requests.Session()
    url = get_root_address(url)
    query = f'{url} "contact emails'

    params = {
    'q': query,     # search query
    'gl': 'us',       # country where to search from   
    'hl': 'en',       # language 
    }

    headers = {
        "Referer":"referer: https://www.google.com/",
        }
    
    ua = UserAgent()
    header = ua.random
    headers['User-Agent'] = header
    request = req.get('https://www.google.com/search', params=params, headers=headers)
    response = request.text
    print(f'{request.url} | {request.status_code}')
    if request.status_code != 200:
        response = dynamic_response(request.url)
    return response

def get_root_address(url):
    """Takes a url and returns the domain
    @param url: Any url like https://example.com/
    @return: returns the domain: example.com
    """
    if not url:
        raise ValueError("URL cannot be null")

    u = urlparse(url)
    return u.netloc
     

def token_counter(response):
        encoding = tiktoken.encoding_for_model('gpt-3.5-turbo-0125')
        return len(encoding.encode(response))

def extract_json(input_string):
    pattern = r'{[^{}]+}' 
    matches = re.findall(pattern, input_string)

    for match in matches:
        try:
            json_data = json.loads(match)
            return json_data
        except json.JSONDecodeError:
            pass

    return None

if __name__ == "__main__":
    url = 'https://shipfa.st/'

    response = html_scraper(url)
    result = gemini_response(response, prompts[0]['find_founder'])
    result = extract_json(result)
    print(result)

    