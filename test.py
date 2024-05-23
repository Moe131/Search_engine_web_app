from bs4 import BeautifulSoup 
import json 

with open("sample/148f711e56e52431552229fd10be1f95eb3171a4d8a500adfa9593d6f772038e.json", 'r') as f:
            # Load the json file into data
            data = json.load(f)
            soup = BeautifulSoup(data['content'], "lxml")
            content = soup.getText()
            print(content)