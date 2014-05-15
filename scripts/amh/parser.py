from lxml import etree
from artwork import Artwork
from jinja2 import Environment, PackageLoader, FileSystemLoader
from xml.sax.saxutils import escape
import sys, json, re

def get_template():
    loader = FileSystemLoader( searchpath = "./" )

    env = Environment(
        block_start_string='<%',
        block_end_string='%>',
        variable_start_string='<%=',
        variable_end_string='%>',
        loader = loader,
        trim_blocks = True,
        lstrip_blocks = True
    )

    return env.get_template('artwork.html')

def get_records(filename):
    tree = etree.parse(filename)
    root = tree.getroot()
    return tree.findall("//record")

if __name__ == "__main__":
    template = get_template()
    records = get_records("./data/kb-indented.xml")

    for record in records:
        # if record.find("priref").text != "6700":
            # continue

        artwork = Artwork(record)
        artwork.process()
        continue

        if artwork.is_valid():
            artwork.process()
            data = artwork.get_data()
            # data["jsondata"] = json.dumps(data)
            # data["xmldata"] = escape(etree.tostring(record))

            html = template.render(data)
            # print json.dumps(data, indent = 4)
            print html
            sys.exit()
        else:
            print "Skipping this one..."