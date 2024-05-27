from engine.posting import Posting
from engine.tokenizer import remove_stop_words
from engine.indexer import Indexer
from porter2stemmer import Porter2Stemmer
import json, sys, math

inverted_index_path = "data/inverted_index.txt"
index_of_index_path = "data/indexOfIndex.json"
document_ids_path = "data/documentIDs.json"
doc_summaries_path = "data/docSummaries.json"
query_freq = {} # Keeps track of how many times a query token has been searched
cache = {} 

class Engine(object):
    """Represents the engine of the search engine"""
    def __init__(self):
        self.inverted_index_file = None  # Dictionary of tokens and their postings
        self.documents = {}  # Dictionary of URL and their IDs
        self.doc_summaries = {}  # Dictionary of doc IDs and their title and summaries
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
            with open(doc_summaries_path, "r") as f2:
                for key, value in json.load(f2).items():
                    self.doc_summaries[int(key)] = value

        except FileNotFoundError:
            # If the file doesn't exist
            self.documents = {}
            self.index_of_index = {}
            self.doc_summaries = {}


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

    def record_query(self, query):
        """ Records a query and the number of times it has been searched in a dictionary for caching """
        for token in query:
            if token in query_freq:
                query_freq[token] += 1
            else:
                query_freq[token] = 1

    def process(self, query):
        """Processes the query by using the inverted index and returns a list of URLs in order of relevance to the query"""
        # Stemming the search query words
        search_result = list()
        stemmer = Porter2Stemmer()
        query = remove_stop_words(query)
        query = [stemmer.stem(q.lower()) for q in query.split()]
        # Keep track of query words' frequencies
        self.record_query(query)

        query_idfs = {}
        query_postings = {}
        for word in query:
            if word in self.index_of_index:
                postings = self.find_postings(word, self.index_of_index[word])
                # Saving the idf of this query word
                query_idfs[word] = idf = math.log10(len(self.documents)/len(postings))
                query_postings[word] = postings
        
        # Sorts the search results by their cosine similarity score to query
        search_result = sorted(self.calculate_relevance_score(query, query_idfs ,query_postings).items(), key=lambda x:x[1], reverse=True)
        search_result = [res[0] for res in search_result]
        return search_result
    

    def calculate_relevance_score(self, query, query_idfs ,query_postings):
        """ Computes the relevance score for a query and all given postings"""
        field_scores = {}
        cosine_scores = {}
        proximity_scores = {}
        positions = {}
        length = {}
        for word in query:
            if word in self.index_of_index:
                postings = query_postings[word]
                for p in postings:
                    #calculating field score
                    fields_score = self.calculate_fields_score(p)
                    if p.docID in field_scores:
                        field_scores[p.docID] += fields_score
                    else:
                        field_scores[p.docID] = fields_score
                    
                    #calculating cosine similarity
                    weight = query_idfs[word] * p.tfidf
                    if p.docID in cosine_scores:
                        cosine_scores[p.docID] += weight
                    else:
                        cosine_scores[p.docID] = weight
                    if p.docID in length:
                        length[p.docID] += p.tfidf*p.tfidf 
                    else:
                        length[p.docID] = p.tfidf*p.tfidf
                    
                    # store the positioning of tokens
                    if len(p.positions) == 0:
                        continue
                    if p.docID in positions:
                        positions[p.docID][word] = p.positions
                    else:
                        positions[p.docID] = dict()
                        positions[p.docID][word] = p.positions

        relevance_scores = dict()
        query_length = math.sqrt(sum(idf * idf for idf in query_idfs.values()))
        # Completing the calculation of cosine similarity score
        for docID,score in cosine_scores.items():
            cosine_scores[docID] = cosine_scores[docID] / ( query_length  *  math.sqrt(length[docID]) )
        
        # Only keeping the top K documents with highest cosine similarity and field scores for calculation of relevance score
        K = 100
        cosine_scores = dict(sorted(cosine_scores.items(), key=lambda x: field_scores[x[0]] + x[1], reverse=True)[:K])

        for docID,score in cosine_scores.items():
            # Calculate proximity score
            proximity_scores[docID] = self.calculate_proximity_score(query, positions[docID]) if len(positions[docID]) > 1 else 0
            # Relevacne score for each document
            relevance_scores[docID] = cosine_scores[docID] + field_scores[docID] + proximity_scores[docID]
        return relevance_scores
            

    def calculate_fields_score(self , posting):
        """ Calculates the score for postings by checking if the query token is in title, h1 or bolded tags"""
        score = 0
        fields = posting.fields.split()
        if 'title' in fields:
            score += 0.5
        if 'h1' in fields:
            score += 0.3
        if 'bold' in fields:
            score += 0.2
        return score
    

    def calculate_proximity_score(self, query, token_positions):
        """ Calculates the proximity score of a documents given the positions of query tokens in that document """
        score = 0
        proximity = len(query) + 1
        first_token = next(iter(token_positions))
        first_positions = set(token_positions[first_token])
        del token_positions[first_token]
        # check for proximity for positioning of each tokens
        for token, positions in token_positions.items():
            for pos in positions:
                # Check proximity around each position
                if any(abs(pos - t) < proximity for t in first_positions):
                    score += 1 / ( len(positions) * proximity )
        return score
    

    def calculate_cosine_similarity(self, query, query_idfs ,query_postings):
        """ Calculates cosine similairty score for a query and all the postings containing the query words 
        and returns a dictionary of document IDs and their similarity scores"""
        scores = {}
        length = {}
        for word in query:
            if word in self.index_of_index:
                postings = query_postings[word]
                idf = query_idfs[word]
                for p in postings:
                    weight = idf * p.tfidf
                    if p.docID in scores:
                        scores[p.docID] += weight
                    else:
                            scores[p.docID] = weight

                    if p.docID in length:
                        length[p.docID] += p.tfidf*p.tfidf 
                    else:
                        length[p.docID] = p.tfidf*p.tfidf
    
        query_length = math.sqrt(sum(idf * idf for idf in query_idfs.values()))

        for doc,score in scores.items():
            scores[doc] = scores[doc] / ( query_length  *  math.sqrt(length[doc]) )
        return scores


    def find_intersection(self, postings_list):
        """Finds the intersection of a list of postings by joining them and returning a set of posting IDs that are present in all"""
        # Find and use the shortest list for intersection
        shortest_list = min(postings_list, key=len)
        other_lists = sorted([p for p in postings_list if p != shortest_list], key= len)
        result = set()
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
                result.add(posting.docID)

        return result


    def get_top_results(self, docIDs):
        """Gets a list of docIDs as parameter and displays the top five them in order"""
        THRESHOLD = 5 # Max number of results to show
        result = list() # list of url, title and summary for each postings 
        for i in range(len(docIDs)):
            if i >= THRESHOLD:
                break
            result.append(list())
            url = self.documents[docIDs[i]]
            title = self.doc_summaries[docIDs[i]].rsplit(":",1)[0] if docIDs[i] in self.doc_summaries else "No Title"
            summary = self.doc_summaries[docIDs[i]].rsplit(":",1)[1] if docIDs[i] in self.doc_summaries else ""
            result[i].append(url) # url
            result[i].append(title) # title
            result[i].append(summary) # summary
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
