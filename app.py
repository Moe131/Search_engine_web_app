from flask import Flask, render_template, request, redirect, url_for
from engine import Engine
from engine import Posting
import time

app = Flask(__name__)
engine = Engine()
# Search query
query = ""
search_results = []
has_searched = False
# time for each query
query_time = 0


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
    app.run()