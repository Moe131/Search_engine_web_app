from flask import Flask, render_template, request, redirect, url_for
from engine import Engine
from engine import Posting

app = Flask(__name__)
engine = Engine()
# Search query
query = ""
search_results = []

@app.route("/", methods=["POST", "GET"])
def index():
    global query, search_results
    if request.method == "POST":
        query = request.form['query']
        postings = engine.process(query)
        search_results = engine.get_top_five(postings)
        print(search_results)
        return redirect('/')
    else:
        return render_template('index.html', urls = search_results)

if __name__ == "__main__":
    app.run()