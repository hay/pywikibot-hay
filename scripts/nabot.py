#!/usr/bin/python
from replacebot import ReplaceBot
import pywikibot, re, replacebot, util, nalib

class NaBot( ReplaceBot ):
    def __init__(self, generator, dry):
        super(NaBot, self).__init__(generator, dry)
        # Set the edit summary message
        self.summary = "Robot: Adding a Nationaal Archief license template, then removing the manual added category"

    def replacer(self, text, page):
        pywikibot.output("====" * 20)

        pywikibot.output(u"Working on %s" % page.title(asLink = True))

        result = nalib.anefo_replacer(text)

        if result.success:
            pywikibot.output( result.outputMessage )
            self.summary = result.summary
            return result.text
        else:
            pywikibot.output( result.outputMessage )
            return False

if __name__ == "__main__":
    try:
        replacebot.main( NaBot )
    finally:
        pywikibot.stopme()
