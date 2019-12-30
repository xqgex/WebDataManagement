#!/usr/bin/python
# -*- coding: utf-8 -*-
####### Code written in Python 2 #######
import sys, urllib2, unicodedata, rdflib
from rdflib import XSD
from bs4 import BeautifulSoup

Q_STRINGS = ["who is the {relation} of {entity}?",
		 "what is the {relation} of {entity}?",
		 "when was {entity} born?"]
Q_STRINGS_list = [None]*3
WIKI_URL = "https://en.wikipedia.org/w/index.php?search="
ONTOLEGY_FILE = "ontolegy.nt"
QUERY_FILE = "query.sparql"
EXAMPLE_URL = "https://yogev.nati.com/"

def getUrl(url):
	for indx in range(5): # Try up to 5 times
		try:
			html = urllib2.urlopen(url)
			return (html.read(), html.url)
		except:
			pass
	return None

def cleanText(input_lst):
	ret = []
	for input_str in input_lst:
		bad_chars = [["[","]"], ["(",")"]]
		for bad_char in bad_chars:
			while bad_char[0] in input_str:
				start_pos = input_str.index(bad_char[0]) # First char position
				end_pos = input_str.index(bad_char[1]) # First char position
				input_str = input_str[:start_pos] + input_str[end_pos+1:]
		ret.append(input_str.strip())
	return ret

def extractCapital(row_td, row_content):
	tmp = []
	for child in row_td.findAll():
		if child.name == "span" and child.has_attr("class") and "plainlinks" in child["class"]:
			break
		tmp.append(child)
	for t in tmp:
		if t.name == "a":
			row_content.append(
				unicodedata.normalize("NFKD", t.get_text())
					.encode('ascii', errors='ignore').replace("\n", " ").strip())

def extractEntityFromUrl(url):
	return url.split("/")[-1]

def infoboxOfEntity(entity):
	direct_try = "+".join(entity)
	page, url = getUrl(WIKI_URL+direct_try)
	if not page:
		return [{}, "", "{} - Failed to connect Wikipedia website, Check your internet connection and try again.".format(" ".join(entity))]
	soup = BeautifulSoup(page, "html.parser")
	try:
		infobox_html = soup.find("div",{"class":"mw-parser-output"}).find("table",{"class":"infobox"})
	except:
		return [{}, "", "{} - Failed to parse Wiki page, There is no 'infobox' table.".format(" ".join(entity))]
	infobox = {}
	for row in infobox_html.findAll("tr"):
		try:
			row_title = row.find("th").get_text()
		except:
			continue # Skip infobox images and sub-tables
		try:
			row_td = row.find("td")
			test_for_errors = row_td.get_text()
		except:
			continue # Skip page title
		row_title = unicodedata.normalize("NFKD", row_title).encode('ascii',errors='ignore').replace("\n"," ").lower().strip()
		if 0 < len(row_title): # Ignore fields without a title
			row_content = []
			if "capital" in row_title: # Capital needs special handling, due to the fact that the landmark of the capital also appears in the same row
				extractCapital(row_td, row_content)
			elif row_td.find("li"): # In case there are several options, Ex. Barack Obama Parents
				for li in row_td.findAll("li"):
					row_content.append(unicodedata.normalize("NFKD", li.get_text()).encode('ascii',errors='ignore').replace("\n"," ").strip())
			else:
				row_content.append(unicodedata.normalize("NFKD", row_td.get_text()).replace("\n", " ").strip())
			infobox[row_title] = cleanText(row_content)
	return [infobox, extractEntityFromUrl(url), ""]

def createRelationList(input_str):
	ret = [input_str]
	if 0 < len(input_str): # To be on the safe side
		if "(" in input_str:
			ret.append(input_str.split("(")[0].strip())
		if input_str[-1] == "s":
			ret.append(input_str[:-1])
		else:
			ret.append("{}s".format(input_str))
	return ret

def rephraseQStrings():
	for index in range(len(Q_STRINGS)):
		Q_STRINGS_list[index] = Q_STRINGS[index].split(" ")

def printUsage():
	print "Usage: python wiki_qa.py <natural language question string>\nthe avilable options are:"
	for index in range(len(Q_STRINGS)):
		print "\t {}) python wiki_qa.py {}".format(index+1,Q_STRINGS[index])

def parseInput(argv):
	input_string = [x.lower() for x in argv if len(x) > 0]
	string_type = -1
	queries = []
	for index in range(len(Q_STRINGS)): # Search what type of question is it
		if len(Q_STRINGS_list[index]) <= len(input_string): # Check that the question is long enough
			if ((input_string[0] == Q_STRINGS_list[index][0])and(input_string[1] == Q_STRINGS_list[index][1])and(input_string[-1][-1]=="?")): # Check the first two words and "?" at the end
				if index in [0,1]: # Verify it's "who is the {relation} of {entity}?" or "what is the {relation} of {entity}?"
					if ((input_string[2] == Q_STRINGS_list[0][2])and("of" in input_string[3:])): # Check that the third word is "the" and the question contain at least one "of"
						string_type = index
						input_string[-1] = input_string[-1][:-1] # Remove the last char (we already checked that its "?")
						locations_of = [x for x,v in enumerate(input_string) if v == "of"]
						for location_of in locations_of:
							if input_string[location_of+1] != "the":
								queries.append({"relation":input_string[3:location_of],"entity":input_string[location_of+1:]})
							else: # Remove the word 'the' from the first entity if exists
								queries.append({"relation":input_string[3:location_of],"entity":input_string[location_of+2:]})
				elif index == 2: # Verify it's "when was {entity} born?"
					if input_string[-1] == Q_STRINGS_list[2][-1]: # Check that the last word is "born?"
						string_type = index
						queries.append({"relation":["born"],"entity":input_string[2:-1]})
	return [string_type,queries]

def addToOntolegy(ontolegy, rdfEntity, rdfRelation, value):
	if rdflib.URIRef("born") == rdfRelation:
		rdfVal = rdflib.Literal(EXAMPLE_URL + value, datatype=XSD.string)
	else:
		rdfVal = rdflib.URIRef(EXAMPLE_URL + value.replace(" ", "_")) # URL encoding
	ontolegy.add((rdfEntity, rdfRelation, rdfVal))

def translateQueryToSparql(entity, relation):
	sparqlQuery = "SELECT ?ans WHERE {\n"			# SPARQL Query
	sparqlQuery += "<{}{}> ".format(EXAMPLE_URL, entity)	# <entity>
	sparqlQuery += "<{}{}> ".format(EXAMPLE_URL, relation)	# <relation>
	sparqlQuery += "?ans .\n"				# Returned variable
	sparqlQuery += "}"					# End SPARQL Query

	with open(QUERY_FILE, "w") as queryfile:
		queryfile.write(sparqlQuery)

def main(input_arguments):
	rephraseQStrings()
	parsed_input = parseInput(input_arguments) # Ex. parsed_input = [0, [{'relation': ['prime', 'minister'], 'entity': ['france']}]]
	ontolegy = rdflib.Graph() # Ontolegy of the entity the query referred to.
	wiki_error_show = True
	wiki_error_output = []
	for input_variation in parsed_input[1]: # In case we found several occurrence of the word "of" # Ex. input_variation = {'relation': ['prime', 'minister'], 'entity': ['france']}
		entity_infobox, entity, wiki_error_loop = infoboxOfEntity(input_variation["entity"]) # Ex. entity_infobox = {'president of the senate': [u'Ge\u0301rard Larcher'], 'capital and largest city': ['Paris'], 'prime minister': [u'E\u0301douard Philippe'], ...}
		if 0 < len(wiki_error_loop): # Invalid page or communication error
			wiki_error_output.append(wiki_error_loop)
			continue # Try the next one
		wiki_error_show = False # If at least one of the variation work, don't show those wiki load errors
		relation_str = " ".join(input_variation["relation"]) # Ex. relation_str = "prime minister"
		rdfEntity = rdflib.URIRef(EXAMPLE_URL + entity) # Entity as a URIRef object.
		for loop_relation,loop_value in entity_infobox.iteritems(): # Ex. loop_relation = "capital and largest city" # Ex. loop_value = ['Paris']
			loop_relation_list = createRelationList(loop_relation)
			if relation_str in loop_relation_list:
				our_answer = ", ".join(loop_value)
				print our_answer.encode('utf-8')
				rdfRelation = rdflib.URIRef(EXAMPLE_URL + relation_str.replace(" ", "_")) # Relation, as written in the query, as a URIRef object.
				addToOntolegy(ontolegy, rdfEntity, rdfRelation, our_answer)
				translateQueryToSparql(entity, relation_str.replace(" ", "_"))
			else:
				rdfRelation = rdflib.URIRef(EXAMPLE_URL + loop_relation.replace(" ", "_")) # Relation as a URIRef object.
				for val in loop_value:
					addToOntolegy(ontolegy, rdfEntity, rdfRelation, val)
	if wiki_error_show:
		print "\n".join(wiki_error_output)
	ontolegy.serialize(ONTOLEGY_FILE, format="nt") # Write ontolegy to file.

if __name__ == "__main__":
	if len(sys.argv)>1:
		main(sys.argv[1:])
	else:
		printUsage()

