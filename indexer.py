from bs4 import BeautifulSoup 
import json
import os
from tokenizer import *

# Dictionary of tokens and their postings
inverted_index = {}
# Dictionary of URL and their IDs
URLids = {}

def main():
    # List of all the files in the directory
    files = os.listdir("sample_files") 
    counter = 0

    for file in files : 
        # If file is not JSON do not read it
        if not file.endswith(".json"):
            continue
        with open(f"small_dataset/{file}",) as the_file:
            # Load the json file into data
            data = json.load(the_file) 

            # Save the URL id
            url = data['url']
            URLids[url] = counter;
            counter += 1


if __name__ == "__main__":
    main()

