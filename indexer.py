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
    directory = "sample_files"
    files = os.listdir(directory) 
    counter = 0

    for file in files : 
        # If file is not JSON do not read it
        if not file.endswith(".json"):
            continue
        with open(f"{directory}/{file}",) as the_file:
            # Load the json file into data
            data = json.load(the_file) 

            # Save the URL id
            url = data['url']
            URLids[url] = counter;
            counter += 1

            # Read the content of file
            soup = BeautifulSoup(data['content'], "html.parser")
            content = soup.getText()

            # Tokenize the content and add them to inverted index dictionary
            for token, freq in tokenize(content).items():
                if token in inverted_index:
                    inverted_index[token].append( (URLids[url],freq) )
                else:
                    inverted_index[token] = [(URLids[url],freq)]

    with open("inverse_index.txt", 'w') as f:
        for key, value in inverted_index.items():
            f.write(f"{key} : {value} \n")

if __name__ == "__main__":
    main()

