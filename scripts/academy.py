# -*- coding: utf-8  -*-
import pywikibot, csv, json
site = pywikibot.Site("wikidata", "wikidata")
repo = site.data_repository()
movies = csv.DictReader( open("/Users/hay/htdocs/git/wiki/wikidata-imports/academy-nominees/academy2.csv") )

NOMINATED = u'P1411'
AWARD = u'Q102427'
POINT_IN_TIME = u'P585'
IMPORTED_FROM = u'P143'
EN_WIKI = u'Q328'

for movie in movies:
    qid = movie["wikidata"]
    year = movie["year"]

    if not qid or movie["winner"] == "True":
        continue

    print qid, movie["title"], year

    item = pywikibot.ItemPage(repo, movie["wikidata"])
    item.get()

    # Check if claim exists
    if NOMINATED in item.claims:
        print "Got something already"
        print json.dumps(item.claims[NOMINATED], indent = 4)
        continue

    # Claim
    claim = pywikibot.Claim(repo, NOMINATED)
    target = pywikibot.ItemPage(repo, AWARD)
    claim.setTarget(target)
    item.addClaim(claim)

    # Time qualifier
    qtime = pywikibot.Claim(repo, POINT_IN_TIME)
    qval = pywikibot.WbTime(year = year)
    qtime.setTarget(qval)
    claim.addQualifier(qtime)

    # Source
    source = pywikibot.Claim(repo, IMPORTED_FROM)
    source.setTarget( pywikibot.ItemPage(repo, EN_WIKI) )
    claim.addSource(source)

