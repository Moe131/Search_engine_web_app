from engine.posting import Posting
from engine.indexer import Indexer
from porter2stemmer import Porter2Stemmer
from types import SimpleNamespace
import json, sys, pickle

inverted_index_path = "data.txt" # replace file path with ../data(DEV).pickle for DEV indexed file
index_of_index_path = "indexOfIndex.json"
document_ids_path = "documentIDs.json"

class Engine(object):
    """Represents the engine of the search engine"""
    def __init__(self):
        self.inverted_index = {}  # Dictionary of tokens and their postings
        self.documents = {}  # Dictionary of URL and their IDs
        self.load_data()


    def load_data(self):
        """Loads inverted index and documents from pickle file into the memory"""
        # This is used for temporarily adjusting path for loading the pickle file
        sys.path.append(r'engine') 
        try:
            with open(inverted_index_path, "r") as f:
                    for line in f:
                        parts = line.split(' ', 1)
                        token = parts[0]
                        postings = [Posting.from_json(p) for p in json.loads(parts[1])]
                        self.inverted_index[token] = postings

            with open(document_ids_path, "r") as f:
                for key, value in json.load(f).items():
                    self.documents[int(key)] = value

        except FileNotFoundError:
            # If the file doesn't exist
            self.inverted_index = {}
            self.documents = {}



    def process(self, query):
        """Processes the query by using the inverted index and returns a list of URLs in order of relevance to the query"""
        # Stemming the search query words
        search_result = list()
        stemmer = Porter2Stemmer()
        query_stems = [stemmer.stem(q.lower()) for q in query.split()]

        # If searched is one word long
        if len(query_stems) == 1:
            qstem = query_stems[0]
            if qstem in self.inverted_index:
                search_result = self.inverted_index[qstem]
        # If searched query is two words or more
        elif len(query_stems) >= 2:
            qstem1 = query_stems[0]
            qstem2 = query_stems[1]
            if qstem1 in self.inverted_index and qstem2 in self.inverted_index:
                search_result = self.find_intersection(self.inverted_index[qstem1], self.inverted_index[qstem2])
            for i in range(2, len(query_stems)):
                if query_stems[i] in self.inverted_index:
                    search_result = self.find_intersection(self.inverted_index[query_stems[i]], search_result)
                else:  # If one of the query words is not in the inverted index return empty search result (BOOLEAN Search model)
                    search_result = list()
                    break
        return search_result

    def find_intersection(self, posting1, posting2):
        """Finds the intersection of two lists postings by joining them and returning the list of postings that are present in both"""
        result = list()
        iterator1, iterator2 = iter(posting1), iter(posting2)
        try:
            p1, p2 = next(iterator1), next(iterator2)
            while True:
                if p1.docID == p2.docID:
                    result.append(Posting(p1.docID, p1.tfidf + p2.tfidf))
                    p1, p2 = next(iterator1), next(iterator2)
                elif p1.docID < p2.docID:
                    p1 = next(iterator1)
                else:
                    p2 = next(iterator2)
        except StopIteration:  # In case we reach to end of one of the postings
            pass
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
