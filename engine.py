from indexer import load_inverted_index

# Dictionary of tokens and their postings
inverted_index = {}
# Dictionary of URL and their IDs
URLids = {}

def process(query):
    """ Processes the query by using the inverted index and
      returns a list of URLs in order of relevance to the query"""
    return list()


def display(urls):
    """ Gets a list of result URLs as parameter and displays them in order """
    counter = 1
    for url in urls:
        print(f"{counter}. {url}\n")
        counter += 1


def run():
    """ The search engine starts running and asks the user to enter queries"""
    global inverted_index , URLids
    inverted_index , URLids = load_inverted_index()
    while (True):
        query = input("Enter your search query:     ")
        if query.isspace() or query == "":
            break
        results = process(query)
        display(results)

if __name__ == "__main__":
    run()