#!/usr/bin/python
# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE

TESTS =[
	["Who is the president of Italy?", "Sergio Mattarella"],
	["Who is the spouse of Gal Gadot?", "Yaron Varsano"],
	["What is the alma mater of Gal Gadot?", "IDC Herzliya"],
	["Who is the MVP of the 2011 NBA Finals?", "Dirk Nowitzki"],
	["What is the best picture of the 90th Academy Awards?", "The Shape of Water"],
	["What is the capital of Canada?", "Ottawa"],
	["When was Theodor Herzl born?", "2 May 1860 Pest, Kingdom of Hungary, Austrian Empire"],
	["Who is the parent of Barack Obama?", "Barack Obama Sr., Ann Dunham"],
	["Who is the monarch of Canada?", "Elizabeth II"],
	["What is the capital of Italy?", "Rome"],
	["When was Bar Refaeli born?", "4 June 1985 Hod HaSharon, Israel"],
	["Who is the host of the 89th Academy Awards?", "Jimmy Kimmel"],
	["What is the official language of Israel?", "Hebrew, Arabic"],
	["Who is the parent of Ronald Reagan?", "Jack Reagan, Nelle Wilson Reagan"],
	["What is the government seat of Netherlands?", "The Hague"],
	["What is the position of LeBron James?", "Small forward"], 
	["WHO IS THE presideNt oF united stATEs of ameRIca?", "Donald Trump"],
	["what is the full name of neymar?", "Neymar da Silva Santos Júnior"],
	["who is the prime minister of france?", "Édouard Philippe"],
	["what is the type of order of fiji?", "State Order"],
	["what is the website of Of, Turkey?", "www.of.bel.tr"],
	["who is the speaker of the house of turkey?", "İsmail Kahraman"],
	["When WaS Charlie and the Chocolate Factory (film) born?", ""],
	]

def main():
	for test in TESTS:
		p1 = Popen(["python", "wiki_qa.py"]+test[0].split(" "), stdout=PIPE)
		answer = p1.communicate()[0].strip()
		if answer == test[1]:
			print "#"*20 + " OK " + "#"*20
			expected = ""
		else:
			print "#"*20 + " Failed " + "#"*20
			expected = "\nExpected: {}".format(test[1])
		print "Q: {}\nA: {}{}".format(test[0],answer,expected)

if __name__ == "__main__":
	main()
