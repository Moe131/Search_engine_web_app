import json, os , re
from engine.tokenizer import tokenize
from engine.summarizer import summarize, remove_extra_spaces
from engine.simhash import *
from engine.posting import Posting
from bs4 import BeautifulSoup 

inverted_index_path = "data/inverted_index.txt"
index_of_index_path = "data/indexOfIndex.json"
document_ids_path = "data/documentIDs.json"
doc_summaries_path = "data/docSummaries.json"

class Indexer(object):
    """Represents the indexer for the search engine."""

    def __init__(self, directory ):
        self.inverted_index = {}  # Dictionary of tokens and their postings
        self.documents = {}  # Dictionary of URL and their IDs
        self.counter = 0  # Counts from zero for URL ids
        self.partions_paths = list()
        self.directory = directory # Directory containing the crawled pages
        self.doc_summaries = {} # mapping of document ID to (tilte +  summary)
        self.sim_hashes = set()  # sim hashes of content to detect exact/near duplicate


    def index(self, file):
        """Indexes a JSON file with a given path and stores the inverted index globally as a mapping of a token to a list of tuples of URL ids and frequency"""
        # If file is not JSON do not read it
        if not file.endswith(".json"):
            return
        with open(file, 'r') as f:
            # Load the json file into data
            data = json.load(f)

            # Read the content of file
            soup = BeautifulSoup(data['content'], "lxml")
            content = soup.get_text(separator=" ", strip=True) # Extract the text text = body.get_text()
            content_tokens , token_positions = tokenize(content)

            # tokens in the tilte, h1 , or bold headers
            title_tokens,h1_tokens,bold_tokens = find_title_h1_bold(soup)

            # Check if its exact or near duplicate do not index if it is
            if self.is_duplicate(content_tokens):
                return

            # Save the URL id
            url = data['url']
            self.documents[self.counter] = url
            url_id = self.counter
            self.counter += 1

            # Tokenize the content and add them to inverted index dictionary
            for token, freq in content_tokens.items():
                fields = create_field(title_tokens, h1_tokens, bold_tokens, token) # Checks if token was in title, h1 or strong tags
                position = token_positions[token] # list of the positions that token appeared in text
                if token in self.inverted_index:
                    self.inverted_index[token].append(Posting(url_id, freq, fields, position))
                else:
                    self.inverted_index[token] = [Posting(url_id, freq, fields, position)]

            title = get_title(soup, url)
            try:
            # Summarize the first 1200 character of content using OpenAI and saves it in a file along with the title of documents
                self.doc_summaries[url_id] = title + " : " + summarize(content[:1200])
            except:
                # if OpenAI could not summarize just used to first 100 characters of content
                self.doc_summaries[url_id] = title + " : "  + content.replace(":", " ")[:100] 

    def is_duplicate(self,content):
        """ Checks if the conent is exact or near duplicate of already scraped websites. """
        # store the hash and check if its exat duplicate
        simhash = simHash(content)
        if simhash in self.sim_hashes: # exact dupliacte
            return True
    
        for sh in self.sim_hashes:
            if are_near_duplicate(sh, simhash):
                return True
        # store the hash if its not already stored
        self.sim_hashes.add(simhash)
        return False


    def save_doc_summaries(self, path):
        """ Saves the mapping of document ID and their summaries in a file"""
        with open(path, "w") as f:
            json.dump(self.doc_summaries, f)

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
            print(f"Now indexing {root}.")
            for f in files:
                # If limit exceeded for number of files indexed 
                if directory_counter > limit:
                    self.save_inverted_index(f"data/index_p{partial_index_count}.txt")
                    self.inverted_index = {}
                    directory_counter = 0
                    partial_index_count += 1
                self.index(f"{root}/{f}")
            self.save_doc_summaries(doc_summaries_path) # remove later
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
        print(f"--- All files were indexed. ---")
        self.save_documentIDs(document_ids_path)
        print(f"--- DocumentIDs file saved. ---")
        self.make_index_of_index(index_of_index_path)
        print(f"--- Index of Index file saved. ---")
        self.save_doc_summaries(doc_summaries_path)
        print(f"--- Documents Summary file saved. ---")
        #self.create_report("report.txt")


# HELPER METHODS

def get_title(soup, url):
    """ Excracts the title of pages from content parsed by beautifulsoup"""
    title_tag = soup.find('title')
    title = title_tag.get_text(separator=" ", strip=True) if title_tag else None
    if not title:
        h1_tag = soup.find('h1')
        title = h1_tag.get_text() if h1_tag else url
    return title


def create_field(title_tokens, h1_tokens, bold_tokens, token):
    """ Finds if a token has appeared in the following fields of a page :
    <title> , <h1> , <strong>""" 
    # creating a list of all common heading tags
    result = ""
    if token in title_tokens:
        result += "title "
    if token in h1_tokens:
        result += "h1 "
    if token in bold_tokens:
            result += "bold "
    return result

def find_title_h1_bold(soup):
    """ Find the token in title, h1 and bold tags by iterating through the soup content"""
    title_text = ""
    h1_text = ""
    bold_text = ""  
    for tag in soup.find_all(["title", "h1", "strong", "b"]):
        tag_name = tag.name
        tag_text = tag.get_text()
        if tag_name == "title":
            title_text = tag_text
        elif tag_name == "h1":
            h1_text += tag_text + " "
        elif tag_name in ["strong", "b"]:
            bold_text += tag_text + " "
    title_tokens, positions = tokenize(title_text)
    h1_tokens, positions = tokenize(h1_text)
    bold_tokens, positions = tokenize(bold_text)
    return title_tokens, h1_tokens, bold_tokens