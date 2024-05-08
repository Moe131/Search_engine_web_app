from bs4 import BeautifulSoup 
import json
import os
from tokenizer import *
from nltk.stem import PorterStemmer

# Dictionary of tokens and their postings
inverted_index = {}
# Dictionary of URL and their IDs
URLids = {}
# Counts from zero for URL ids
counter = 0
# Initialize Porter Stemmer
stemmer = PorterStemmer()


def index(file):
    """ Indexes a JSON file with a given path and stores the inverted index
      globaly as a mapping of a token to a list of tuples of URL ids and frequency"""
    global inverted_index, URLids, counter
    # If file is not JSON do not read it
    if not file.endswith(".json"):
        return
    with open(file, 'r') as f:
        # Load the json file into data
        data = json.load(f) 

        # Save the URL id
        url = data['url']
        URLids[counter] = url
        url_id = counter
        counter += 1

        # Read the content of file
        soup = BeautifulSoup(data['content'], "html.parser")
        content = soup.getText()

        # Tokenize the content and add them to inverted index dictionary
        for token, freq in tokenize(content).items():
            if token in inverted_index:
                inverted_index[token].append( (url_id,freq) )
            else:
                inverted_index[token] = [(url_id,freq)]


def save_inverted_index(filepath):
    """ Saves the inverted index dictionary in a txt file"""
    with open(filepath, 'w') as f:
        f.write(f"Number of unique tokens : {len(inverted_index)} \n"+ "-" * 50 + "\n")
        f.write(f"Number of documents  : {len(URLids)} \n"+ "-" * 50 + "\n")
        for key, value in inverted_index.items():
            f.write(f"{key} : {value} \n")


def main():
    # Traverse through directories to find all files
    directory = "sample_files"
    for (root, dirs, files) in os.walk(directory) :
        for f in files:
            index(f"{root}/{f}")
        print(f"All '{root}' directory files were indexed ")
    # Saves the inverted index dictionary in a file
    save_inverted_index("inverse_index.txt")


if __name__ == "__main__":
    main()

