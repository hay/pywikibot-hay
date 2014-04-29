#!/usr/bin/python
# -*- coding: utf-8 -*-
import json, pywikibot, sys, os
from pywikibot import config

description = u"""== Summary ==
{{Artwork
|title =
{{la|1=Theatrum ichnographicum omnium urbium et præcipuorum oppidorum Belgicarum XVII Provinciarum peraccurate delineatarum.}}
{{nl|1=Perfecte aftekeningen der steden van de XVII Nederlandsche Provincien in platte gronden}}
{{fr|1=Le theatre des plans de toutes les villes qui sont situéez dans les XVII Provinces du Pays Bas parfaictement déseignéez}}
|description =
{{nl|1=%s uit het ''Stedenboek'' van Frederick de Wit.}}
{{en|1=%s from the ''Stedenboek'' (citybook) by Frederick de Wit.}}
|author = {{Creator:Frederick de Wit}}
|date = {{other date|ca|1698}}
|object type = Atlas
|medium = Print, coloured by hand
|institution = {{Institution:Koninklijke Bibliotheek}}
|place of creation = Amsterdam, the Netherlands
|permission = {{PD-old-100}}
|accession number = [http://opc4.kb.nl/PPN?PPN=145205088 PPN 145205088]
|source = {{Koninklijke Bibliotheek}}
[http://www.kb.nl/bladerboek/stedenboek/browse/page_%s.html "Bladerboek Stedenboek" at the website of the Koninklijke Bibliotheek]
|wikidata = Q15726418
|other_versions=
}}

[[Category:Frederick de Wit]]%s
[[Category:Atlas de Wit 1698]]"""

class UploadRobot:
    def __init__(self):
        self.targetSite = pywikibot.Site('commons', 'commons')
        self.targetSite.forceLogin()
        self.PATH = os.path.realpath(
            os.path.join(
                os.getcwd(), os.path.dirname(__file__)
            )
        )

    def format(self, img):
        city = img["city"].replace("-", "") if img["city"] != "" else False
        citybr = "(%s)" % city if city else ""
        dsc = (img["id"], citybr)
        category = "\n[[Category:Old maps of %s]]\n" % city if city else ""

        category = category.decode('utf-8')

        text = description % (
            "Plaat '%s'%s" % dsc,
            "Plate '%s'%s" % dsc,
            img["id"],
            category
        )

        return text

    def upload_image(self, img):
        site = self.targetSite
        filename = self.PATH + "/stedenboek/" + img["filename"]
        imagepage = pywikibot.ImagePage(site, img["filename"])  # normalizes filename
        imagepage.text = self.format(img)

        pywikibot.output(u'Uploading file %s to %s via API....' % (img["filename"], site))

        try:
            site.upload(imagepage, source_filename = filename)
        except pywikibot.UploadWarning as warn:
            pywikibot.output(u"We got a warning message: ", newline=False)
            pywikibot.output(str(warn))
        except Exception as e:
            pywikibot.error("Upload error: ", exc_info=True)
        else:
            # No warning, upload complete.
            pywikibot.output(u"Upload successful.")

    def run(self):
        images = json.loads(file(self.PATH + "/kbupload.json", "r").read())

        for img in images:
            self.upload_image(img)


def main(*args):
    pywikibot.handleArgs(*args)
    bot = UploadRobot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
