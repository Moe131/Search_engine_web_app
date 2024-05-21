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
	''' reads in a text and returns a list of the tokens in that string '''
	tokens = dict()
	token = ""
	for ch in text + " ":
		if isAlphaNum(ch):
			token += ch
		else:
			if token != "":
				if  len(token) > 1 :
					word = stemmer.stem(token.lower())
					if word in tokens.keys():
						tokens[word] += 1
					else:
						tokens[word] = 1
				token = "" 
	return tokens