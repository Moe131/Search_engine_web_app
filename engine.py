from indexer import load_inverted_index
from porter2stemmer import Porter2Stemmer
from posting import Posting


# Dictionary of tokens and their postings
inverted_index = {}
# Dictionary of URL and their IDs
documents = {}

def process(query):
    """ Processes the query by using the inverted index and
      returns a list of URLs in order of relevance to the query"""
    #Stemming the search query words
    search_result = list()
    stemmer = Porter2Stemmer()
    query_stems = [stemmer.stem(q.lower()) for q in query.split()]

    # If searched is one word long
    if len(query_stems) == 1:
        qstem = query_stems[0]
        if qstem in inverted_index:
                search_result = inverted_index[qstem]
    # If searched query is two words or more 
    elif len(query_stems) >= 2:
        qstem1 = query_stems[0]
        qstem2 = query_stems[1]
        if qstem1 in inverted_index and qstem2 in inverted_index:
                search_result = find_intersection(inverted_index[qstem1], inverted_index[qstem2])
        for i in range(2, len(query_stems)):
                if query_stems[i] in inverted_index:
                    search_result = find_intersection(inverted_index[query_stems[i]], search_result)
                else: # If one of the query words is not in the inverted index return empty search result ( BOOLEAN Search model)
                     search_result = list()
                     break
    return search_result


def find_intersection(posting1 ,posting2):
    """ Finds the intersection of two lists postings by joining them
      and returning the list of postings that are present in both """
    result = list()
    iterator1, iterator2 = iter(posting1), iter(posting2)
    try:
        p1, p2 = next(iterator1), next(iterator2)
        while(True):
            if p1.docID == p2.docID :
                result.append( Posting(p1.docID, p1.tfidf+ p2.tfidf) )
                p1, p2 = next(iterator1), next(iterator2)
            elif p1.docID < p2.docID:
                p1 = next(iterator1)
            else:
                p2 = next(iterator2)        
    except StopIteration: #In case we reach to end of one of the postings
        pass
    return result


def display(postings):
    """ Gets a list of result URLs as parameter and displays them in order """
    print("-" * 50)
    if len(postings) == 0:
        print("No results found for your query")
        return
    counter = 1
    for p in sorted(postings, key=lambda posting:posting.tfidf, reverse = True): # Shows search results sorted by highest tfidf 
        if (counter > 10): # Show the first 10 search results only
            return
        print(f"{counter}. {documents[p.docID]}\n")
        counter += 1


def run():
    """ The search engine starts running and asks the user to enter queries"""
    global inverted_index , documents
    inverted_index , documents = load_inverted_index("data.pickle") # replace file path with ../data(DEV).pickle for DEV indexed file
    while (True):
        query = input("Enter your search query:     ")
        if query.isspace() or query == "":
            break
        results = process(query)
        display(results)

if __name__ == "__main__":
    run()