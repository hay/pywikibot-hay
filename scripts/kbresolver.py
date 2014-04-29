#!/usr/bin/python
from replacebot import ReplaceBot
import pywikibot, re, replacebot, util, kbresolverlib

"""
python pwb.py kbresolver -pt:60 -search:"kranten.kb.nl/view/article"
"""

class KbResolver( ReplaceBot ):
    def __init__(self, generator, dry):
        super(KbResolver, self).__init__(generator, dry)
        # Set the edit summary message
        self.summary = "Robot: Oude kranten.kb.nl links vervangen door nieuwe resolver.kb.nl links die correct verwijzen naar de nieuwe krantenbank op Delpher.nl"

    def replacer(self, text, page):
        pywikibot.output("====" * 20)

        pywikibot.output(u"Working on %s" % page.title(asLink = True))

        if "kranten.kb.nl/view/article" not in text:
            pywikibot.output("No kranten.kb.nl/view/article references found, skipping")
            return False

        text = kbresolverlib.parse(text)

        pywikibot.output("Replaced old links")

        return text

if __name__ == "__main__":
    try:
        replacebot.main( KbResolver )
    finally:
        pywikibot.stopme()
