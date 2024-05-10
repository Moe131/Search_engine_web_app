from indexer import load_inverted_index
from porter2stemmer import Porter2Stemmer


# Dictionary of tokens and their postings
inverted_index = {}
# Dictionary of URL and their IDs
documents = {}

def process(query):
    """ Processes the query by using the inverted index and
      returns a list of URLs in order of relevance to the query"""
    # Now just handles a single word query
    result = list()
    postings = list()
    stemmer = Porter2Stemmer()
    # For each token in query find its list of postings
    for word in query.split():
        stem = stemmer.stem(word.lower())
        if stem in inverted_index:
            for posting in inverted_index[stem]:
                result.append(posting)
    return result


def display(postings):
    """ Gets a list of result URLs as parameter and displays them in order """
    print("-" * 50)
    if len(postings) == 0:
        print("No results found for your query")
        return
    counter = 1
    for p in postings:
        if (counter > 10): # Show the first 10 search results only
            return
        print(f"{counter}. {documents[p.docID]}\n")
        counter += 1


def run():
    """ The search engine starts running and asks the user to enter queries"""
    global inverted_index , documents
    inverted_index , documents = load_inverted_index()
    while (True):
        query = input("Enter your search query:     ")
        if query.isspace() or query == "":
            break
        results = process(query)
        display(results)

if __name__ == "__main__":
    run()