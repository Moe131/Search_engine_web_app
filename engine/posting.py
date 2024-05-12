
class Posting(object):
    """ Represents a posting in the inverted index table which 
    contains document ID, tf-idf weight, fields , and positions"""
    def __init__(self, docID, tfidf, fileds = None, positions = None):
        self.docID = docID
        self.tfidf = tfidf # frequency for now
        self.fileds = fileds
        self.positions = positions
        