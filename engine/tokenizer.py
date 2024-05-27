from porter2stemmer import Porter2Stemmer

stemmer = Porter2Stemmer()

# Time complexity of this method is constant O(1) because it only
# iterates through a constant sized string
def isAlphaNum(ch:str) -> bool:
    ''' Checks if a character is number or american letter  '''
    english_letters= set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    if ch in english_letters:
        return True
    else:
        return False


# Time complexity of this method is linear  O(n). The method iterates through 
# the characters(bytes) one by one.
def tokenize(text: str) -> dict:
	''' reads in a text and returns two dictionaries: first,
	 1:  token -> frequency , 2: token -> list of positions '''
	tokens = dict()
	positions = dict()
	token = ""
	pos = 1 # keeps track of the position of the token
	for ch in text + " ":
		if isAlphaNum(ch):
			token += ch
		else:
			if token != "":
				if  len(token) > 1 :
					stemed_token = stemmer.stem(token.lower())
					# Update the frequency of the token
					if stemed_token in tokens.keys():
						tokens[stemed_token] += 1
					else:
						tokens[stemed_token] = 1
					# Update the positions of the token
					if stemed_token in positions.keys():
						positions[stemed_token].append(pos)
					else:
						positions[stemed_token] = [pos]
					pos += 1
				token = ""
	return tokens, positions

stopwords = {'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 
             'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 
             'both', 'but', 'by', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', 
             "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 
             "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 
             'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", 
             "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 
			 'more', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 
			 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', "shan't", 'she', 
			 "she'd", "she'll", "she's",'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 
			 'their', 'theirs', 'them', 'themselves','then', 'there', "there's", 'these', 'they', "they'd", "they'll", 
			 "they're", "they've", 'this', 'those', 'through', 'to','too', 'under', 'until', 'up', 'very', 'was', "wasn't", 
			 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's", 'where', "where's", 
			 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 'you', "you'd", 
			 "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves'}


def remove_stop_words(query):
	""" Removes the stop words from query if the query is not entirely made of stop words """
	update_query = ""
	for word in query.split():
		if word not in stopwords:
			update_query += word + " "
	if len(update_query.split()) >= 2:
		return update_query
	else:
		return query