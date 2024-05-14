import json, os, pickle
from engine.tokenizer import tokenize
from engine.posting import Posting
from porter2stemmer import Porter2Stemmer
from bs4 import BeautifulSoup 

inverted_index_path = "data.txt"
index_of_index_path = "indexOfIndex.json"
document_ids_path = "documentIDs.json"

class Indexer(object):
    """Represents the indexer for the search engine."""

    def __init__(self, directory ):
        self.inverted_index = {}  # Dictionary of tokens and their postings
        self.documents = {}  # Dictionary of URL and their IDs
        self.counter = 0  # Counts from zero for URL ids
        self.directory = directory # Directory containing the crawled pages


    def index(self, file):
        """Indexes a JSON file with a given path and stores the inverted index globally as a mapping of a token to a list of tuples of URL ids and frequency"""
        # If file is not JSON do not read it
        if not file.endswith(".json"):
            return
        with open(file, 'r') as f:
            # Load the json file into data
            data = json.load(f)

            # Save the URL id
            url = data['url']
            self.documents[self.counter] = url
            url_id = self.counter
            self.counter += 1

            # Read the content of file
            soup = BeautifulSoup(data['content'], "lxml")
            content = soup.getText()

            # Tokenize the content and add them to inverted index dictionary
            stemmer = Porter2Stemmer()
            for token, freq in tokenize(content).items():
                stem = stemmer.stem(token)
                if stem in self.inverted_index:
                    self.inverted_index[stem].append(Posting(url_id, freq))
                else:
                    self.inverted_index[stem] = [Posting(url_id, freq)]

    def create_report(self, path):
        """Creates a report of the inverted index in a text file"""
        with open(path, 'w') as f:
            f.write(f"Number of unique tokens : {len(self.inverted_index)} \n" + "-" * 50 + "\n")
            f.write(f"Number of documents  : {len(self.documents)} \n" + "-" * 50 + "\n")
            # Gets file size of the inverted index
            data_file_size = os.path.getsize(inverted_index_path)
            f.write(f"Inverted Index file size  : {data_file_size/1024} KB\n" + "-" * 50 + "\n")

    def save_inverted_index(self, path):
        """Saves the inverted index in a JSON file"""
        with open(path, "w") as f:
            for token, postings in self.inverted_index.items():
                f.write(token + " " + json.dumps([p.to_json() for p in postings]) + '\n' )


    def save_documentIDs(self,path):
        """Saves the inverted index in a JSON file"""
        with open(path, "w") as f:
            json.dump(self.documents, f)
    

    def make_index_of_index(self,path):
        """ Create the index of index and stores it on disk"""
        line_counter = 0
        mapping = {}
        with open(inverted_index_path, "r") as f1:
            with open(path, "w") as f2:
                for line in f1:
                    parts = line.split(' ', 1)
                    token = parts[0]
                    json.dump({token : line_counter},f2)
                    line_counter += 1


    def run(self):
        # Traverse through directories to find all files
        for (root, dirs, files) in os.walk(self.directory):
            for f in files:
                self.index(f"{root}/{f}")
            print(f"All '{root}' directory files were indexed ")
        self.save_inverted_index(inverted_index_path)
        self.save_documentIDs(document_ids_path)
        self.make_index_of_index(index_of_index_path)
        self.create_report("report.txt")
        print(f"--- All files were indexed. ---")

