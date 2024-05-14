# Search Engine Web Application

This is a simple web application built using Flask for searching documents indexed by a search engine.

## Installation

1. Clone this repository to your local machine:
```
 git clone <repository_url>
```

2. Install the required dependencies:
```
pip install Flask
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
