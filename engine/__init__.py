from engine.posting import Posting
from engine.tokenizer import remove_stop_words
from engine.indexer import Indexer
from porter2stemmer import Porter2Stemmer
import json, sys, math

inverted_index_path = "data/inverted_index.txt"
index_of_index_path = "data/indexOfIndex.json"
document_ids_path = "data/documentIDs.json"
query_freq = {} # Keeps track of how many times a query token has been searched
cache = {} 

class Engine(object):
    """Represents the engine of the search engine"""
    def __init__(self):
        self.inverted_index_file = None  # Dictionary of tokens and their postings
        self.documents = {}  # Dictionary of URL and their IDs
        self.index_of_index = {}
        self.load_files()
        self.open_inverted_index()


    def open_inverted_index(self):
        """Loads inverted index and documents from pickle file into the memory"""
        # This is used for temporarily adjusting path for loading the pickle file
        sys.path.append(r'engine') 
        try:
             self.inverted_index_file = open(inverted_index_path, "r")
        except :
            # If the file doesn't exist
            print("Inverted Index file could not be opened")
            self.inverted_index_file = None


    def __del__(self):
        """ Engine destructor to make sure to closes the inverted index file"""
        if self.inverted_index_file is not None:
            self.inverted_index_file.close()


    def load_files(self):
        """Loads index of index and documents from pickle file into the memory"""
        # This is used for temporarily adjusting path for loading the pickle file
        sys.path.append(r'engine') 
        try:
            with open(index_of_index_path, "r") as f1:
                for key, value in json.load(f1).items():
                    self.index_of_index[key] = int(value)
            with open(document_ids_path, "r") as f2:
                for key, value in json.load(f2).items():
                    self.documents[int(key)] = value
        except FileNotFoundError:
            # If the file doesn't exist
            self.documents = {}
            self.index_of_index = {}


    def find_postings(self, token ,lineNumber):
        """ Finds the postings of a token by loading the inverted index """
        # first check if token and its postings are in cache
        if token in cache:
            return cache[token]
        
        # if token is not in cache look into the inverted index file
        self.inverted_index_file.seek(lineNumber)
        parts = self.inverted_index_file.readline().split(' ',1)
        if token == parts[0]:
            postings = [Posting.from_json(p) for p in json.loads(parts[1])]
            # If token has been searched 5 times or more, add its listings to cache
            if query_freq[token] >= 5:
                cache[token] = postings 
            return postings
        else:
            return list()


    def process(self, query):
        """Processes the query by using the inverted index and returns a list of URLs in order of relevance to the query"""
        # Stemming the search query words
        search_result = list()
        stemmer = Porter2Stemmer()
        query = remove_stop_words(query)
        query_words = [stemmer.stem(q.lower()) for q in query.split()]

        # Keep track of query words' frequencies
        for token in query_words:
            if token in query_freq:
                query_freq[token] += 1
            else:
                query_freq[token] = 1
        
        # Sorts the search results by their cosine similarity score to query
        search_result = sorted(self.calculate_cosine_similarity(query_words).items(), key=lambda x:x[1], reverse=True)
        search_result = [res[0] for res in search_result]
        return search_result


    def calculate_cosine_similarity(self, query):
        """ Calculates cosine similairty score for a query and all the documents containing the query words 
        and returns a dictionary of document IDs and their similarity scores"""
        scores = {}
        length = {}
        query_idfs = []
        for word in query:
            if word in self.index_of_index:
                    word_postings = self.find_postings(word, self.index_of_index[word])
                    # Saving the idf of this query word
                    idf = math.log10(len(self.documents)/len(word_postings))
                    query_idfs.append(idf)
                    for p in word_postings:
                        weight = idf * p.tfidf
                        if p.docID in scores:
                            scores[p.docID] += weight
                        else:
                            scores[p.docID] = weight
                        if p.docID in length:
                            length[p.docID] += p.tfidf*p.tfidf 
                        else:
                            length[p.docID] = p.tfidf*p.tfidf
    
        query_length = math.sqrt(sum(idf * idf for idf in query_idfs))

        for doc,score in scores.items():
            scores[doc] = scores[doc] / ( query_length  *  math.sqrt(length[doc]) )
        return scores



    def find_intersection(self, postings_list):
        """Finds the intersection of a list of postings by joining them and returning the list of postings that are present in all"""
        # Find and use the shortest list for intersection
        shortest_list = min(postings_list, key=len)
        other_lists = sorted([p for p in postings_list if p != shortest_list], key= len)
        result = []
        iterators = [iter(pl) for pl in other_lists]
    
        for posting in shortest_list:
            current_docID = posting.docID
            tfidf_sum = posting.tfidf  # Initialize with the tfidf from the shortest list
        # Check if the current document ID exists in all other posting lists
            in_all = True
            for i, iterator in enumerate(iterators):
                while True:
                    try:
                        other_posting = next(iterator)
                        if other_posting.docID == current_docID:
                            tfidf_sum += other_posting.tfidf
                            break
                        elif other_posting.docID > current_docID:
                            in_all = False
                            break
                    except StopIteration:
                        in_all = False
                        break
                if not in_all:
                    break
            if in_all:
                result.append(Posting(posting.docID, tfidf_sum/len(postings_list)))
        # If the intersection of all words in the query does not have enough results, find the intersection with the last query word removed
        THRESHOLD = 5
        if len(result) < THRESHOLD: 
            return self.find_intersection(postings_list[:len(postings_list)-1])
        else:
            return result


    def get_top_results(self, docIDs):
        """Gets a list of docIDs as parameter and displays the top five them in order"""
        THRESHOLD = 5 # Max number of results to show
        result = list()
        for i in range(THRESHOLD):
            result.append(self.documents[docIDs[i]])
        return result
    

    def run(self):
        """The search engine starts running and asks the user to enter queries"""
        while True:
            query = input("Enter your search query:     ")
            if query.isspace() or query == "":
                break
            results = self.process(query)
            self.display(results)


if __name__ == "__main__":
    engine = Engine()
    engine.run()
