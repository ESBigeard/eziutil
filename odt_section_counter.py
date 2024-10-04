#!/usr/bin/python
# -*- coding:utf-8 -*-

import zipfile
import sys
import re
import xml.etree.ElementTree as ET
from collections import defaultdict


#used on .ODT files
#creates a tree structure of the document's sections and gives the word count for each section, sub-section, etc.

#there's a little bug remaining that inserts spaces in the middle of titles. but i can't be bothered to fix it
#this bug can change the word count if there are style changes in the middle of a word

def text_cleaner(text):
	"""converts text to list of words, removes non-alphanumeric characters, then removes empty words. used to remove non-words that mess with word count"""
	if text is None:
		return []
	if type(text)==str:
		text=text.split(" ")
	text2=[]
	for word in text:
		word=re.sub("[\W]+","",word)
		if len(word)>0:
			text2.append(word)
	return text2

def number_print(a):
	""" converts int to string like 12 345 678"""
	a=str(a)
	if len(a)>6:
		a=a[:-6]+" "+a[-6:]
	if len(a)>3:
		a=a[:-3]+" "+a[-3:]
	return a



def main(filename,encoding="utf-8"):
	archive = zipfile.ZipFile(filename, 'r')
	f= archive.open("content.xml")
	all_document=""
	for l in f:
		l=str(l,encoding=encoding)
		#weird issue where python's string type identifer ends up inside the string
		if l.startswith("b\'"):
			l=l[2:]
		l=l.replace("\\n'","\n")
		l=l.replace("\'","") #solves possible parser error that makes the xml invalid
		all_document+=l
	tree=ET.fromstring(all_document)

	debug=False

	lens_current=defaultdict(int) #stores the length of all currently open levels. after each paragraph, add its len to all opened level. when a level is closed, its len is reset to zero
	lens_current[0]=0 #init root
	previous_level=0
	current_section_len=0
	previous_id={0:0} #d[level]=section id. stores the id of all currently open levels

	#those 3 variables store the output data. 
	all_titles={0:"root"} #d[id]="title of part 1"
	all_levels={0:0} #d[id]=level ex. d[23]=2
	all_lens={0:0} #d[id]=len ex. d[23]=34000

	id_=0
	for tag in tree.iter():

		#we're on a title
		#matches the 'outline-level' in <text:h text:style-name="Heading_20_5" text:outline-level="5">
		if "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}outline-level" in tag.attrib:
			id_+=1
			level=int(tag.get("{urn:oasis:names:tc:opendocument:xmlns:text:1.0}outline-level"))
			title=text_cleaner(tag.text) #title here contains only the text directly at the level of the title. but some part of the text can be in a child of this. happens if the title is edited later. here we search for those children
			for child in tag: #here ideally it should be recursive. it only looks for 1 level of children. it's sufficient in my tests. i need to experiments with doing a lot of edits with different formatting to see if it can generate several levels of children
				text=text_cleaner(child.text)
				if text:
					title+=text
				tail=text_cleaner(child.tail)
				if tail:
					title+=tail
			tail=text_cleaner(tag.tail)
			if tail:
				title+=tail #bug that introduces spaces in the middle of titles if they've been edited
			title=" ".join(title)
			all_titles[id_]=title
			all_levels[id_]=level
			if debug:
				print("title - lvl",level, "| id", id_, title)
				print("len of the previous section",current_section_len) #current_section_len is actually the len of the previous section



			#first, add the text of this section to all open levels
			for level_stashed in lens_current:
				lens_current[level_stashed]+=current_section_len
				if debug:
					print("stashing",level_stashed,current_section_len,lens_current[level_stashed])

			#next, compare current level to the last known level, to see if we need to open/close sub-levels

			#current level is the same as previous one. easy case
			if level==previous_level:
				all_lens[id_-1]=current_section_len #ce qu'on a actuellement dans current_section_len, c'est la len de la section qui se ferme ici, donc la précédente
				#all_titles et all_levels sont déjà remplis au début de la boucle
				#on vide les infos de ce level, prep pour le suivant
				current_section_len=0
				lens_current[level]=0

			#current level is BIGGER than the previous one
			elif level<previous_level:
				#which means we just finished sub-levels, maybe several at the same time
				#close them
				for level_stashed in list(lens_current.keys()): #to avoid size changed during iteration error
					if level_stashed >= level: #this is either a sub-level of the section we are now closing, OR be the section we are closing itself
						len_=lens_current[level_stashed]
						if len_>0:
							prev_id=previous_id[level_stashed] # get id of section
							all_lens[prev_id]=len_ #all len of this section to output
							#lens_current[level_stashed]=0 #empty the level -> bug if we keep it at zero without deleting the entry : at the end, when the script closes the last open levels, it will find this and think it's open, and give it the len of the very last section of the document
						lens_current.pop(level_stashed) #empty and deleted the level
							

				#then open the next up-level
				current_section_len=0
				lens_current[level]=0


			elif level>previous_level: #current level is UNDER the previous level
				if current_section_len>1: #an empty section still has one empty word
					#special case : we open sub-level 1.1 but there was some text under title 1 before opening 1.1 so we create a section 1.0 without any title
					id_2=id_-0.5 # so-called section 1.0 must be BEFORE 1.1 and "id" is the id of 1.1
					all_titles[id_2]="no title"
					all_levels[id_2]=level
					all_lens[id_2]=current_section_len
					lens_current[level]+=current_section_len
					current_section_len=0

				else:
					#open 1.1 right after 1. zero len to add to 1
					pass

			previous_id[level]=id_
			previous_level=level
		
		#normal text
		#BUG/TODO: this also catches comments and counts them as words
		words=text_cleaner(tag.text)
		if words:
			#print(len(words),words)
			current_section_len+=len(words)
		words=text_cleaner(tag.tail)
		if words:
			if debug:
				print(len(words))
			current_section_len+=len(words)




	#add last paragraph length to all open sections
	for level_stashed in lens_current:
		lens_current[level_stashed]+=current_section_len
		#print(level_stashed,current_section_len,lens_current[level_stashed])

	#finish all the open levels
	for level in lens_current:
		len_=lens_current[level]
		if len_>0:
			#we know that level N is open, and has X words
			#need to find the ID of the title linked to it -> the last one added at the correct level
			i_id=max(all_titles)
			while i_id>=0: #go up the titles list
				local_level=all_levels[i_id]
				if local_level==level:
					#found the right title
					if debug:
						print("going up",i_id,len_)
					all_lens[i_id]=len_
					break
				i_id-=1

		
	print()
	for id_ in sorted(all_titles.keys()):
		if id_ in all_lens:
			len_=number_print(all_lens[id_])
		else: #should not happen, but bug catching
			len_="X"
		title=all_titles[id_]
		level=all_levels[id_]
		indent="\t"*level
		print(indent,len_,title)

if __name__=="__main__":
	
	main(sys.argv[1])
