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
    stemmer = Porter2Stemmer()
    for word in query.split():
        stem = stemmer.stem(word.lower())
        if stem in inverted_index:
            for docID,freq in inverted_index[stem]:
                result.append(documents[docID])
    return result


def display(urls):
    """ Gets a list of result URLs as parameter and displays them in order """
    print("-" * 50)
    if len(urls) == 0:
        print("No results found for your query")
        return
    counter = 1
    for url in urls:
        if (counter > 10): # Show the first 10 search results only
            return
        print(f"{counter}. {url}\n")
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