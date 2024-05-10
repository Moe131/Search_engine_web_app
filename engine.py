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
    while (True):
        query = input("Enter your search query:     ")
        if query.isspace() or query == "":
            break
        results = process(query)
        display(results)

if __name__ == "__main__":
    run()