import openai
from bs4 import BeautifulSoup 
import json 
import re

# Directly set the OpenAI API key
api_key = "sk-proj-5A9Gzm4M5nuaxMiiWJcsT3BlbkFJTjzycbzLRb5R2262SFn3"  # Replace with your actual API key
openai.api_key = api_key

def summarize(content):
    """ Creates a 25-word summary of content parameter and returns it """
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "Summarize website content in 20 words"
        },
        {
            "role": "user",
            "content": content
        }
    ],
    temperature=0.7,
    max_tokens=20,
    top_p=1
    )
    return response['choices'][0]['message']['content']

def remove_extra_spaces(text):
    # Remove extra whitespace using regular expressions
    cleaned_text = re.sub(r'\s+', ' ', text.strip())
    return cleaned_text
