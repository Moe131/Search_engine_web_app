from flask import Flask, render_template, request, redirect, url_for
from engine import Engine
from engine import Posting

app = Flask(__name__)
engine = Engine()
# Search query
query = ""
search_results = []
has_searched = False


@app.route("/", methods=["POST", "GET"])
def index():
    global query, search_results, has_searched
    # If the request method is POST (from clicking Search) show results
    if request.method == "POST":
        query = request.form['query']
        # If query is space or empty do not show results
        if query.isspace() or query == "":
            return redirect('/')
        postings = engine.process(query)
        search_results = engine.get_top_five(postings)
        has_searched = True
        return render_template('index.html', urls = search_results, has_searched=has_searched )
    # If the request method is GET (initial page load) Do not show search result
    elif request.method == "GET":
        has_searched = False
        return render_template('index.html', urls = search_results, has_searched=has_searched )
    else:
        return render_template('index.html', urls = search_results, has_searched=has_searched )


if __name__ == "__main__":
    app.run()