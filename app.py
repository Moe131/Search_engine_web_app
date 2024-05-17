from flask import Flask, render_template, request, redirect, url_for
from engine import Engine, Indexer
import time
import sys

# This is the path of the directory containing JSON files to index --> replace
JSON_FILES_PATH = "/Users/mohammadmirzaei/Documents/UCI/Spring24/CS121/Assignmet3(private)/DEV"


app = Flask(__name__)
engine = Engine()
query = ""       # Search query
search_results = []
has_searched = False
query_time = 0 # time for each query



@app.route("/", methods=["POST", "GET"])
def index():
    global query, search_results, has_searched, query_time
    
    # If the request method is POST (from clicking Search) show results
    if request.method == "POST":
        query = request.form['query']
        # If query is space or empty do not show results
        if query.isspace() or query == "":
            return redirect('/')
        start = time.time()
        postings = engine.process(query)
        search_results = engine.get_top_five(postings)
        has_searched = True
        # Calculate the query time
        end = time.time()
        query_time = int((end - start)*1000)
        return render_template('index.html', urls = search_results, has_searched=has_searched, query=query, query_time = query_time )
    
    # If the request method is GET (initial page load) Do not show search result
    elif request.method == "GET":
        has_searched = False
        return render_template('index.html', urls = search_results, has_searched=has_searched, query=query , query_time = query_time )
    
    else:
        return render_template('index.html', urls = search_results, has_searched=has_searched, query=query , query_time = query_time)


if __name__ == "__main__":
    # run the indexer not the app with command : 'python3 app.py index'
    if len(sys.argv) > 1 and sys.argv[1] == "index":
        indexer = Indexer(JSON_FILES_PATH)
        indexer.run()
    else:
        app.run()