class Posting:
    """ Represents a class for each posting in inverted index table which 
    contains document ID, tf-idf weight, fields , and positions"""
    def __init__(self, docID, tfidf, fileds = None, positions = None):
        self.docID = docID
        self.tfidf = tfidf
        self.fileds = fileds
        self.positions = positions