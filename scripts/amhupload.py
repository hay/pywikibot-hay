#!/usr/bin/python
# -*- coding: utf-8 -*-
import json, pywikibot, sys, os
from pywikibot import config
from amh.parser import genamh

class UploadRobot:
    def __init__(self):
        self.targetSite = pywikibot.Site('commons', 'commons')
        self.targetSite.forceLogin()
        self.PATH = os.path.realpath(
            os.path.join(
                os.getcwd(), os.path.dirname(__file__)
            )
        )

    def page_exists(self, filename):
        name = "File:%s" % filename

        try:
            page = pywikibot.Page(self.targetSite, name).get()
        except:
            return False
        else:
            return True

    def upload_image(self, html, data, imgfile):
        site = self.targetSite

        # Construct the name
        commons_filename = "AMH-%s-%s_%s.jpg" % (
            data["amh_id"],
            data["institution_shortcode"].upper(),
            data["title_en"][:150]
        )

        if self.page_exists(commons_filename):
            pywikibot.output("%s already exists, skipping" % commons_filename)
            return

        imagepage = pywikibot.ImagePage(site, commons_filename)  # normalizes filename
        imagepage.text = html

        pywikibot.output(u'Uploading file %s to %s via API....' % (commons_filename, site))

        try:
            site.upload(imagepage, source_filename = imgfile)
        except pywikibot.UploadWarning as warn:
            pywikibot.output(u"We got a warning message: ", newline=False)
            pywikibot.output(str(warn))
        except Exception as e:
            pywikibot.error("Upload error: ", exc_info=True)
        else:
            # No warning, upload complete.
            pywikibot.output(u"Upload successful.")

    def run(self):
        for kind in ("kb", "na"):
            iterator = genamh(self.PATH + "/amh/data/%s-indented.xml" % kind)
            index = 0

            for html, data in iter(iterator):
                # Does we have an image file for this record?
                imgfile = "%s/amh/%s-images/%s" % (self.PATH, kind, data["image_filename"])

                if os.path.isfile(imgfile):
                    self.upload_image(html, data, imgfile)
                    index += 1
                else:
                    print "No image file..." + imgfile
                    sys.exit()
                    continue

                if index > 5:
                    break

def main(*args):
    pywikibot.handleArgs(*args)
    bot = UploadRobot()
    bot.run()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
