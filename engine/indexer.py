import json, os
from engine.tokenizer import tokenize
from engine.posting import Posting
from porter2stemmer import Porter2Stemmer
from bs4 import BeautifulSoup 

inverted_index_path = "data/inverted_index.txt"
index_of_index_path = "data/indexOfIndex.json"
document_ids_path = "data/documentIDs.json"

class Indexer(object):
    """Represents the indexer for the search engine."""

    def __init__(self, directory ):
        self.inverted_index = {}  # Dictionary of tokens and their postings
        self.documents = {}  # Dictionary of URL and their IDs
        self.counter = 0  # Counts from zero for URL ids
        self.partions_paths = list()
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
            for token, freq in tokenize(content).items():
                if token in self.inverted_index:
                    self.inverted_index[token].append(Posting(url_id, freq))
                else:
                    self.inverted_index[token] = [Posting(url_id, freq)]


    def create_report(self, path):
        """Creates a report of the inverted index in a text file"""
        with open(path, 'w') as f:
            f.write(f"Number of unique tokens : {len(self.inverted_index)} \n" + "-" * 50 + "\n")
            f.write(f"Number of documents  : {len(self.documents)} \n" + "-" * 50 + "\n")
            # Gets file size of the inverted index
            data_file_size = os.path.getsize(inverted_index_path)
            f.write(f"Inverted Index file size  : {data_file_size/1024} KB\n" + "-" * 50 + "\n")


    def save_inverted_index(self, path):
        """Saves the sorted inverted index in a JSON file"""
        # sort the inverted index by keys :
        self.inverted_index = dict(sorted(self.inverted_index.items()))
        with open(path, "w") as f:
            for token, postings in self.inverted_index.items():
                f.write(token + " " )
                f.write(json.dumps([p.update_tfidf(len(postings), len(self.documents)).to_json() for p in postings]) )
                f.write('\n')


    def save_documentIDs(self,path):
        """Saves the inverted index in a JSON file"""
        with open(path, "w") as f:
            json.dump(self.documents, f)
    

    def make_index_of_index(self,path):
        """ Create the index of index and stores it on disk"""
        byte_counter = 0
        index_of_index = {}
        with open(inverted_index_path, "r") as f1:
            for line in f1:
                    parts = line.split(' ', 1)
                    index_of_index[parts[0]] = byte_counter
                    byte_counter += len(line.encode('utf-8'))
        with open(path, "w") as f2:
            json.dump(index_of_index, f2)


    def make_index_partitions(self):
        """ Divides the directory of JSON files into 3 parts and 
        creates inverse index partitions out of them"""
        limit = len(os.listdir(self.directory)) / 3 
        directory_counter = 0
        partial_index_count = 1
        for (root, dirs, files) in os.walk(self.directory):
            for f in files:
                # If limit exceeded for number of files indexed 
                if directory_counter > limit:
                    self.save_inverted_index(f"data/index_p{partial_index_count}.txt")
                    self.inverted_index = {}
                    directory_counter = 0
                    partial_index_count += 1
                self.index(f"{root}/{f}")
            directory_counter += 1
            print(f"Directory {root} successfully indexed.")
        # create the last partition
        self.save_inverted_index(f"data/index_p{partial_index_count}.txt")
        self.inverted_index = {}


    def merge_all_partitions(self, path1, path2, path3, dest):
        """ Merges the 3 different partitions into one inverse index file on disk"""
        with open(path1) as f1, open(path2) as f2, open(path3) as f3, open(dest, 'w') as dest_file:
            line1, line2, line3 = f1.readline(), f2.readline(), f3.readline()

            while line1 or line2 or line3:
                token1, token2, token3 = "", "", ""
                posting1, posting2, posting3 = [], [], []

                if line1:
                    token1, posting1 = line1.split(' ', 1)
                    posting1 = [Posting.from_json(p) for p in json.loads(posting1)] if posting1 else []
                if line2:
                    token2, posting2 = line2.split(' ', 1)
                    posting2 = [Posting.from_json(p) for p in json.loads(posting2)] if posting2 else []
                if line3:
                    token3, posting3 = line3.split(' ', 1)
                    posting3 = [Posting.from_json(p) for p in json.loads(posting3)] if posting3 else []

                # Find the minimum token to write the index in a sorted way
                tokens = [token1, token2, token3]
                min_token = min(t for t in tokens if t)

                # If all all partitions have the same token merege the postings lists
                merged_postings = []
                if token1 == min_token:
                    merged_postings.extend(posting1)
                    line1 = f1.readline()
                if token2 == min_token:
                    merged_postings.extend(posting2)
                    line2 = f2.readline()
                if token3 == min_token:
                    merged_postings.extend(posting3)
                    line3 = f3.readline()

                # Write merged postings to the destination file
                dest_file.write(min_token + " ")
                dest_file.write(json.dumps([p.update_tfidf(len(merged_postings), len(self.documents)).to_json() for p in merged_postings]))
                dest_file.write('\n')


    def run(self):
        dataExist = os.path.exists("data")
        if not dataExist: # Create a new directory to hold indexing data
            os.makedirs("data") 
        self.make_index_partitions()
        self.merge_all_partitions("data/index_p1.txt","data/index_p2.txt" ,"data/index_p3.txt",inverted_index_path)
        self.save_documentIDs(document_ids_path)
        self.make_index_of_index(index_of_index_path)
        #self.create_report("report.txt")
        print(f"--- All files were indexed. ---")

