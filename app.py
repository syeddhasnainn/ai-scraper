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

def get_html(playwright: Playwright, url):
    chromium = playwright.chromium
    browser = chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(url)
    html = page.content()
    browser.close()
    return html


def gemini_scraper(url):
    with sync_playwright() as playwright:
        playwright_response = get_html(playwright, url)

    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    print('getting response...')
    response = model.generate_content([f'your are a pro webs scrapign expert, get these fields from the input: {fields_to_scrape}. output should be in a nice json format. Only json nothing else.\n',playwright_response])
    print(response.candidates[0].content.parts[0].text)

def gemini_response(response, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    print('getting response...')
    response = model.generate_content([f'{prompt}: output should be in a nice json format. Only json nothing else.\n',response])
    return response.candidates[0].content.parts[0].text

def html_scraper(query):
    req = requests.Session()

    params = {
    'q': query, # search query
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
    print(request.url)
    return request.text

def token_counter(response):
        encoding = tiktoken.encoding_for_model('gpt-3.5-turbo-0125')
        return len(encoding.encode(response))

if __name__ == "__main__":
    query = 'mentign.com "founder email" ".com"'
    response = html_scraper(query)

    result = gemini_response(response, prompts[0]['find_founder'])
    print(result)
    