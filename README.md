# Search Engine Web Application

This is a search engine web application built using Flask that allows searching over 56,000 websites.

![Screen Shot 2024-06-04 at 17 37 17](https://github.com/Moe131/Search_engine_web_app/assets/65834335/149dae72-ce48-45da-9a30-044a88af5abd)


## Features
- Comprehensive Search: Search across a vast database of 56,000 University of California, Irvine webpages.
- User-Friendly Interface: Intuitive and easy-to-use interface for efficient searching.
- Fast and Reliable: Optimized for quick and accurate search results.
- Document Indexing: Indexes documents and creates an inverted index for efficient search retrieval.
- Summarized Results: Retrieves document summaries using the OpenAI API for quick content insights.
  
## Installation

1. Clone this repository to your local machine:
```
 git clone <repository_url>
```

2. Install the required dependencies:
```
pip install Flask

pip install beautifulsoup4
```
3. Create inverse index for the search engine : 
```
python app.py index
```

4. Run the application:
```
python app.py
```

## Usage

1. Visit `http://localhost:5000/` in your web browser.
2. Enter a search query in the input field and click on the Search button.
3. The top five search results will be displayed along with the time taken for the query.

## File Structure

- `app.py`: Contains the Flask application code.
- `engine.py`: Contains the engine and indexer classes.
- `templates/index.html`: HTML template for the user interface.
