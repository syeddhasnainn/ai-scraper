import json
from dotenv import load_dotenv
import streamlit as st
import os 
import requests
from config import OpenAIConfig

load_dotenv()

def main():
  scraper = OpenAIConfig()
  # st.title('AI Scraper')
  # st.subheader('made by [hasnain](https://x.com/syeddhasnainn)')
  r = requests.Session()
  req = r.get('https://mentign.com/contacts/')
  response = req.text
  response = response[response.find('<header'):response.find('</header>')]  

  data = scraper.get_data(response)
  print(data)
  
if __name__ == '__main__':
  main()    