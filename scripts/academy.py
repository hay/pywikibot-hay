# -*- coding: utf-8  -*-
import pywikibot, csv, json, sys, time, os
site = pywikibot.Site("wikidata", "wikidata")
repo = site.data_repository()
PATH = os.path.realpath(
    os.path.join(
        os.getcwd(), os.path.dirname(__file__)
    )
)
movies = csv.DictReader( open(PATH + "/datasets/academy2.csv") )

NOMINATED = u'P1411'
AWARD = u'Q102427'
AWARD_PROP = u'P166'
POINT_IN_TIME = u'P585'
IMPORTED_FROM = u'P143'
EN_WIKI = u'Q328'

for index, movie in enumerate(movies):
    qid = movie["wikidata"]
    year = int(movie["year"])

    if not qid:
        continue

    print index, qid, movie["title"], year

    if year > 1960:
        print "That's it folks"
        sys.exit()

    item = pywikibot.ItemPage(repo, movie["wikidata"])
    item.get()

    # Check if claim exists
    if (NOMINATED in item.claims) or (AWARD_PROP in item.claims):
        print "%s (%s) nominated or awarded already" % (movie["title"], year)
        continue

    # Claim
    if movie["winner"]:
        claim = pywikibot.Claim(repo, NOMINATED)
    else:
        claim = pywikibot.Claim(repo, AWARD_PROP)

    target = pywikibot.ItemPage(repo, AWARD)
    claim.setTarget(target)
    item.addClaim(claim, summary = u'Bot: Adding claim with academy award nomination.')

    # Time qualifier
    qtime = pywikibot.Claim(repo, POINT_IN_TIME)
    qval = pywikibot.WbTime(year = year)
    qtime.setTarget(qval)
    claim.addQualifier(qtime, summary = u'Bot: Adding a time qualifier for academy nomination')

    # Source
    source = pywikibot.Claim(repo, IMPORTED_FROM)
    source.setTarget( pywikibot.ItemPage(repo, EN_WIKI) )
    claim.addSource(source, summary = u'Bot: Adding an import statement for the claim')

    # Sleep for a bit
    time.sleep(10)
