import urllib2, sys
import lxml.html as HtmlParser

FILE_OUTPUT = "./question5c.txt"
DATA = [{"subsection":"a", "title":"Image sources with non-empty 'alt'",	"string":"//img[not(@alt='') and @alt]/@src", 			"result":""},
	{"subsection":"b", "title":"Links to .co.il domains",			"string":"//a[contains(@href, '.co.il')]/@href", 		"result":""},
	{"subsection":"c", "title":"Content of second row in first table",	"string":"//table[1]/descendant::tr[2]/descendant::*/text()", 	"result":""},
	{"subsection":"d", "title":"All italic words",				"string":"//i/text()", 						"result":""}]

def getUrl(url):
	for indx in range(5): # Try up to 5 times
		try:
			html = urllib2.urlopen(url)
			return html.read()
		except:
			pass
	return None

def print_to_file():
	with open(FILE_OUTPUT, 'w') as outfile:
		for indx in range(len(DATA)):
			outfile.write("{}:\n[\n".format(DATA[indx]["title"]))
			for itm in DATA[indx]["result"]:
				outfile.write("{}\n".format(itm))
			outfile.write(']\n')

def main(url):
	print "Get {}".format(url)
	html = getUrl(url)
	if html:
		print "Parse the website"
		doc = HtmlParser.fromstring(html)
		xpath_dic = []
		for indx in range(len(DATA)):
			print "Scrap website for {}".format(DATA[indx]["title"])
			DATA[indx]["result"] = doc.xpath(DATA[indx]["string"])
		print_to_file()
	else:
		print "Failed to get the requested website"

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Invalid call"
	else:
		main(sys.argv[1])
