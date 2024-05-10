import json, os, pickle
from tokenizer import *
from bs4 import BeautifulSoup 
from porter2stemmer import Porter2Stemmer


# Dictionary of tokens and their postings
inverted_index = {}
# Dictionary of URL and their IDs
URLids = {}
# Counts from zero for URL ids
counter = 0


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
        soup = BeautifulSoup(data['content'], "lxml") 
        content = soup.getText()

        # Tokenize the content and add them to inverted index dictionary
        stemmer = Porter2Stemmer()
        for token, freq in tokenize(content).items():
            stem = stemmer.stem(token)
            if stem in inverted_index:
                inverted_index[stem].append( (url_id,freq) )
            else:
                inverted_index[stem] = [(url_id,freq)]


def create_report(filepath):
    """ Creates a report of the inverted index in a text file"""
    with open(filepath, 'w') as f:
        f.write(f"Number of unique tokens : {len(inverted_index)} \n"+ "-" * 50 + "\n")
        f.write(f"Number of documents  : {len(URLids)} \n"+ "-" * 50 + "\n")
        # Gets file size of the inverted index
        data_file_size = os.path.getsize("data.pickle")
        f.write(f"Inverted Index file size  : {data_file_size/1024} KB\n"+ "-" * 50 + "\n")


def save_inverted_index():
    """ Saves the inverted index dictionaries in a pickle file """
    with open("data.pickle", "wb") as f:
        pickle.dump((inverted_index, URLids), f)


def load_inverted_index(): 
     """ Loads the inverted index dictionaries from the pickle file and returns them"""
     try:
        with open("data.pickle" , "rb") as f:
            inverted_index, URLids = pickle.load(f)
     except FileNotFoundError:
        # If the file doesn't exist
        inverted_index = {}
        URLids = {}
     return inverted_index, URLids



def main():
    # Repalce with the file path of DEV directory in your system
    directory = "sample"
    # Traverse through directories to find all files
    for (root, dirs, files) in os.walk(directory) :
        for f in files:
            index(f"{root}/{f}")
        print(f"All '{root}' directory files were indexed ")
    save_inverted_index()
    create_report("report.txt")
    print(f"--- All files were indexed. ---")


if __name__ == "__main__":
    main()

