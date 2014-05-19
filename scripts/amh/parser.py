from lxml import etree
from artwork import Artwork
from jinja2 import Environment, PackageLoader, FileSystemLoader
from xml.sax.saxutils import escape
import sys, json, re
from locations import get_locations

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
    records = get_records("./data/na-indented.xml")
    locations = get_locations()

    for record in records:
        artwork = Artwork(record, locations)

        if artwork.is_valid():
            artwork.process()
            data = artwork.get_data()

            if "nodata" not in sys.argv:
                data["jsondata"] = json.dumps(data)
                data["xmldata"] = escape(etree.tostring(record))

            html = template.render(data).strip()
            # print json.dumps(data, indent = 4)
            print html
            sys.exit()
        else:
            print "Skipping this one..."