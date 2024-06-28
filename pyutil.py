#!usr/bin/python
# -*- coding:utf-8 -*-
"""various usefull functions"""

import unicodedata, re, codecs, os
path = os.path.dirname(os.path.realpath(__file__))+"/"

def normalise_unicode(s,diac=True):
	"""normalise a string toward a standard unicode string, w/ or w/o diacritics

	normalise une chaine vers une unicode string standard, avec ou sans diacritiques

	:param arg1: string to normalise
	:type arg1: str or unicode
	:param arg2: True to keep diacritics, False to delete them. Default : keep them
	:type arg2: bool

	:example:
	>>> fun.normalise_unicode(u"\\xc3\\xa9ternel",True)
	u"\\xe9ternel"
	"""
	#note : if you look at the code of the example above, the double backslashes are escaped single backslashes. those are to be read as single backslashes

	try:
		s=unicode(s)
	except UnicodeDecodeError:
		s=s.decode("utf-8")
	

	if diac:
		nf=unicodedata.normalize('NFKC',s)
	else:
		nf=unicodedata.normalize('NFKD',s)
	nf=nf.replace(u'\u0153','oe')
	nf=nf.replace(u'\u00B7','.') #puce RCP
	nf=nf.replace(u'\u2019',"'") #apostrophe RCP
	#nf=nf.replace(u'\u2028',' ') #line separator

	if False : #normaliser les whitespaces
		nf2=""
		for char in nf:
			if not re.match(u"\s",char,re.UNICODE) or char in ["\n"," "]:
				nf2+=char
		return u''.join(c for c in nf2 if not unicodedata.combining(c))

	if diac:
		return nf
	else:
		return u''.join(c for c in nf if not unicodedata.combining(c))
	
	
def empty_tree(input_list):
	"""Recursively iterate through values in nested lists to check if the structure is empty
	
	from http://stackoverflow.com/questions/1593564
	
	:type arg1: list
	:return: True if the structure is empty, false otherwise
	:rtype: bool"""
	for item in input_list:
		if not isinstance(item, list) or not empty_tree(item):
			return False
	return True
	


def chunker(s,keep_delimiters=True):
	"""
	split a string, intended to split french text. keep delimiters, keep groups of dots or numbers together, keep ' attached to previous word, keep aujourd'hui and peut-etre as single groups

	split une string, utiliser pour split du texte en francais. conserve les separateurs, garde les groupes de points ou de chiffres ensemble, colle ' au mot precedent, aujourd'hui et peut-etre restent en un seul mot

	:param arg1: string to split
	:type arg1: str or unicode
	:return: list of unicode strings
	:rtype: list

	:example:
	>>> fun.chunker("j'ai vu un lama aujourd'hui... qu'il etait beau!")
	["j'"," ","ai"," ","vu"," ","un"," ","lama"," ","aujourd'hui","..."," ","qu'","il","etait","beau","!"]

	"""
	s=s.replace(u"\u2019","'") #apostrophe RCP
	s=re.split("(\s+|\.+|\W|\d+)",s,flags=re.UNICODE) #les groupes de whitespace de . ou groupes de chiffres sont laissés ensemble, le reste séparé
	s2=[]
	i=-1 #compteur de mots
	while i < len(s)-1:
		i+=1
		e=s[i] #e = mot en cours

		if e and len(e)>0:
			if s2 : #s'il existe au moins un char précédent

				if e=="'": #coller les apostrophes au mot précédent
					if s2[-1].endswith("'"): #double ' utilisée comme guillemets
						#TODO traiter mieux que ça les apostrophes multiples
						s2[-1]=s2[-1][:-1]
						s2.append("''")
					else:
						s2[-1]+="'"
				#elif s2[-1]=="$": #remonter les codes type $med
				#	s2[-1]="$"+e
				else: #pour que aujourd'hui soit traité après l'apostrophe
					if s2[-1]=="aujourd'":
						s2[-1]+=e
					elif len(s2)>1 and  s2[-2]=="peut" and s2[-1]=="-" and e in ["etre",u"être"]:
						s2.pop()#tiret
						s2.pop()#peut
						s2.append("peut-etre")
					else:
						s2.append(e)

			else:
				s2.append(e)
	
	if not keep_delimiters:
		s3=[]
		for w in s2:
			if re.match(" +$",w):
				pass
			else:
				s3.append(w)
		return s3
	return s2

def join_treetagger(fname,col=2):
	"""open a treetagger output file and join the text. default output the lemmatized text"""
	
	with codecs.open(fname,"r","utf-8") as f:
		text=[]
		for l in f:
			l=l.rstrip()
			l=l.split("\t")
			try:
				word=l[col]
				text.append(word)
			except IndexError:
				pass
	return " ".join(text)
	

def merge(lsts):
	"""
	merge a list of lists into a list of sets, where all lists sharing at least one element are merged. used to merge sub-syntagms

	fusionne une liste de listes en une liste de sets, où les listes ayant au moins 1 élément en commun sont fusionnées. utilisé pour merge les sous-syntagmes
	
	:param arg1: list of lists to merge
	:type arg1: list
	:return: list of merged sets
	:rtype: list of sets
	
	:example:
	>>> fun.merge([[0,1,2],[2,3],[4,5]])
	[set([0,1,2,3]),set([4,5])]
	
	"""
	
	sets = [set(lst) for lst in lsts if lst]
	merged = 1
	while merged:
		merged = 0
		results = []
		while sets:
			common, rest = sets[0], sets[1:]
			sets = []
			for x in rest:
				if x.isdisjoint(common):
					sets.append(x)
				else:
					merged = 1
					common |= x
			results.append(common)
		sets = results
	return sets

def fmesure(rappel,pre):
	return 2*((pre*rappel)/(pre+rappel))







