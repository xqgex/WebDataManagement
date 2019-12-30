from question3a import *
import unicodedata
import os.path

ONTOLEGY = rdflib.Graph()
if os.path.isfile(GRAPH_FILE):
    ONTOLEGY.parse(GRAPH_FILE, format="nt")
else:
    print("File not found; extracting data from {}".format(START_LINK))
    ONTOLEGY = buildOntolegy()


def printQueryResult(res):
    for row in res:
        s = ""
        for r in row:
            s += (r + "     ")
        print(unicodedata.normalize('NFKD', s).encode('ascii','ignore'))


# Section b
# Queries: for each subsection x, qx is the respective query
qa = "SELECT ?p ?t WHERE {" \
     "?p <" + RELATIONS[STR_BIRTH_PLACE] + "> ?city ." \
     "?city <" + RELATIONS[STR_LOCATED_IN] + "> $country ." \
     "FILTER regex(lcase(STR(?country)), 'spain')" \
     "?p <" + RELATIONS[STR_PLAYS_FOR] + "> ?t ." \
     "?t <" + RELATIONS[STR_LEAGUE] + "> <http://example.org/Premier_League> ." \
     "}"
print("Subsection a:")
printQueryResult(ONTOLEGY.query(qa))

qb = "SELECT ?p ?t WHERE {" \
     "?p <" + RELATIONS[STR_PLAYS_FOR] + "> ?t ." \
     "?p <" + RELATIONS[STR_BIRTH_DATE] + "> ?date ." \
     "FILTER(STR(?date) > STR('http://example.org/1990-12-31')) ." \
     "}"
print("\nSubsection b:")
printQueryResult(ONTOLEGY.query(qb))

qc = "SELECT ?p WHERE {" \
     "?p <" + RELATIONS[STR_PLAYS_FOR] + "> ?t ." \
     "?p <" + RELATIONS[STR_BIRTH_PLACE] + "> ?c ." \
     "?t <" + RELATIONS[STR_HOME_CITY] + "> ?c ." \
     "}"
print("\nSubsection c:")
printQueryResult(ONTOLEGY.query(qc))

qd = "SELECT ?t1 ?t2 WHERE {" \
     "?t1 <" + RELATIONS[STR_HOME_CITY] + "> ?c ." \
     "?t2 <" + RELATIONS[STR_HOME_CITY] + "> ?c ." \
     "FILTER(STR(?t1) < STR(?t2)) ." \
     "}"
print("\nSubsection d:")
printQueryResult(ONTOLEGY.query(qd))