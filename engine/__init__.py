from engine.posting import Posting
from engine.indexer import Indexer
from porter2stemmer import Porter2Stemmer
import json, sys

inverted_index_path = "data.txt" # replace file path with ../data(DEV).pickle for DEV indexed file
index_of_index_path = "indexOfIndex.json"
document_ids_path = "documentIDs.json"

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
        self.inverted_index_file.seek(lineNumber)
        parts = self.inverted_index_file.readline().split(' ',1)
        if token == parts[0]:
            return [Posting.from_json(p) for p in json.loads(parts[1])]
        else:
            return list()


    def process(self, query):
        """Processes the query by using the inverted index and returns a list of URLs in order of relevance to the query"""
        # Stemming the search query words
        search_result = list()
        stemmer = Porter2Stemmer()
        query_stems = [stemmer.stem(q.lower()) for q in query.split()]

        # If searched is one word long
        if len(query_stems) == 1:
            qstem = query_stems[0]
            if qstem in self.index_of_index:
                search_result = self.find_postings(qstem, self.index_of_index[qstem])
        # If searched query is two words or more
        elif len(query_stems) >= 2:
            postings = list()
            for q in query_stems:
                if q not in self.index_of_index:
                    return list()
                else:
                    postings.append(self.find_postings(q, self.index_of_index[q]))
            search_result = self.find_intersection(postings)
        return search_result

    def find_intersection(self, postings_list):
        """Finds the intersection of a list of postings by joining them and returning the list of postings that are present in all"""
        # Find and use the shortest list for intersection
        shortest_list = min(postings_list, key=len)
        other_lists = [p for p in postings_list if p is not shortest_list]

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
                result.append(Posting(posting.docID, tfidf_sum))
        
        return result


    def display(self, postings):
        """Gets a list of result URLs as parameter and displays them in order"""
        print("-" * 50)
        if len(postings) == 0:
            print("No results found for your query")
            return
        counter = 1
        for p in sorted(postings, key=lambda posting: posting.tfidf, reverse=True):  # Shows search results sorted by highest tfidf
            if counter > 10:  # Show the first 10 search results only
                return
            print(f"{counter}. {self.documents[p.docID]}\n")
            counter += 1

    def get_top_five(self, postings):
        """Gets a list of result URLs as parameter and displays the top five them in order"""
        result = []
        counter = 1
        for p in sorted(postings, key=lambda posting: posting.tfidf, reverse=True):  # Shows search results sorted by highest tfidf
            if counter > 5:  # Show the first 10 search results only
                break
            result.append(self.documents[p.docID])
            counter += 1
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
