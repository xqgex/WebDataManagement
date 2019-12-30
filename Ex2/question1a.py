import urllib2, sys
from bs4 import BeautifulSoup

DB = {}
FILE_OUTPUT = "./question1c.txt"

def save():
	with open(FILE_OUTPUT, 'w') as outfile:
		for site,site_links in DB.iteritems():
			outfile.write("{} = {{{}}}\n".format(site, ", ".join(site_links)))
			print "{} = {{{}}}".format(site, ", ".join(site_links))

def getUrl(url):
	for indx in range(7):
		try:
			html = urllib2.urlopen("https://en.wikipedia.org{}".format(url))
			return html.read()
		except:
			pass
	return None

def crawl(start_url, depth):
	page = getUrl(start_url)
	if page:
		internal_count = 0
		soup = BeautifulSoup(page, "html.parser")
		urls = soup.findAll("a")
		for url in urls:
			if url.has_attr("href"):
				loop_url = url["href"].split("#")[0]
				if internal_count < 10:
					if ("/wiki/" == loop_url[:6].lower()) and (":" not in loop_url):
						if depth < 2:
							if loop_url not in DB:
								internal_count += 1
								DB[start_url].add(loop_url)
								DB[loop_url] = set()
								crawl(loop_url, depth+1)
						elif (depth == 2) and (loop_url in DB) and (loop_url not in DB[start_url]):
							internal_count += 1
							DB[start_url].add(loop_url)
				else:
					break

def main(start_url):
	if "wikipedia.org" in start_url:
		start_url = start_url.split("wikipedia.org")[1].split("#")[0]
		if ":" not in start_url:
			DB[start_url] = set()
			crawl(start_url, 0)
			save()
		else:
			print "{} is not a valid wikipedia url".format(start_url)
	else:
		print "{} is not a valid wikipedia url".format(start_url)

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Invalid call"
	else:
		main(sys.argv[1])
