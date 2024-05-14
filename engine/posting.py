import json

class Posting:
    """ Represents a posting in the inverted index table which 
    contains document ID, tf-idf weight, fields , and positions"""
    def __init__(self, docID, tfidf, fields=None, positions=None):
        self.docID = docID
        self.tfidf = tfidf  # frequency for now
        self.fields = fields
        self.positions = positions
    
    def to_json(self):
        return {
            "docID": self.docID,
            "tfidf": self.tfidf,
            "fields": self.fields,
            "positions": self.positions
        }
    
    @classmethod
    def from_json(cls, json_data):
        return cls(
            int(json_data.get("docID")),
            float(json_data.get("tfidf")),
            json_data.get("fields"),
            json_data.get("positions")
        )