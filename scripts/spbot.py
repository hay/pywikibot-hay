#!/usr/bin/python
from readonlybot import ReadonlyBot
import pywikibot, readonlybot

data = {
    "sp" : [],
    "nonsp" : []
}

class SpBot( ReadonlyBot ):
    def __init__(self, generator, dry):
        super(SpBot, self).__init__(generator, dry)

    def process(self, page, text):
        title = page.title()

        pywikibot.output("Processing %s" % title)

        if "spaarnestad photo" in text.lower():
            data["sp"].append( title )
        else:
            data["nonsp"].append( title)

def writelist(name, f):
    f.write("<h1>%s</h1>\n<ul>\n" % name)

    for link in data[name]:
        line = '<li><a href="http://commons.wikimedia.org/wiki/%s">%s</a></li>\n' % (link, link)
        f.write(line.encode('utf-8'))

    f.write('</ul>\n')

if __name__ == "__main__":
    try:
        readonlybot.main( SpBot )
        html = open("spbot.html", "w")
        html.write("<!doctype html><meta charset=utf-8>")
        writelist("sp", html)
        writelist("nonsp", html)
    finally:
        pywikibot.stopme()
