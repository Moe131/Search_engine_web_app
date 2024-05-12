import json, os, pickle
from engine.tokenizer import tokenize
from engine.posting import Posting
from porter2stemmer import Porter2Stemmer
from bs4 import BeautifulSoup 



class Indexer(object):
    """Represents the indexer for the search engine."""

    def __init__(self):
        self.inverted_index = {}  # Dictionary of tokens and their postings
        self.documents = {}  # Dictionary of URL and their IDs
        self.counter = 0  # Counts from zero for URL ids

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

    def create_report(self, filepath):
        """Creates a report of the inverted index in a text file"""
        with open(filepath, 'w') as f:
            f.write(f"Number of unique tokens : {len(self.inverted_index)} \n" + "-" * 50 + "\n")
            f.write(f"Number of documents  : {len(self.documents)} \n" + "-" * 50 + "\n")
            # Gets file size of the inverted index
            data_file_size = os.path.getsize("data.pickle")
            f.write(f"Inverted Index file size  : {data_file_size/1024} KB\n" + "-" * 50 + "\n")

    def save_inverted_index(self):
        """Saves the inverted index dictionaries in a pickle file"""
        with open("data.pickle", "wb") as f:
            pickle.dump((self.inverted_index, self.documents), f)


    def run(self):
        # Replace with the file path of DEV directory in your system
        directory = "sample"
        # Traverse through directories to find all files
        for (root, dirs, files) in os.walk(directory):
            for f in files:
                self.index(f"{root}/{f}")
            print(f"All '{root}' directory files were indexed ")
        self.save_inverted_index()
        self.create_report("report.txt")
        print(f"--- All files were indexed. ---")


if __name__ == "__main__":
    indexer = Indexer()
    indexer.run()