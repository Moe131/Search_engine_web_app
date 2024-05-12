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
    if request.method == "POST":
        query = request.form['query']
        postings = engine.process(query)
        search_results = engine.get_top_five(postings)
        has_searched = True
        return redirect('/')
    else:
        return render_template('index.html', urls = search_results, has_searched=has_searched )

if __name__ == "__main__":
    app.run()