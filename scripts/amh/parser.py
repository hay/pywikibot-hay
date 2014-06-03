from lxml import etree
from artwork import Artwork
from jinja2 import Environment, PackageLoader, FileSystemLoader
from xml.sax.saxutils import escape
import sys, json, re, os
from locations import get_locations

PATH = os.path.realpath(
    os.path.join(
        os.getcwd(), os.path.dirname(__file__)
    )
)

def get_template():
    loader = FileSystemLoader( searchpath = PATH )

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

def genamh(filename):
    template = get_template()
    records = get_records(filename)
    locations = get_locations()

    for record in records:
        artwork = Artwork(record, locations)

        if not artwork.is_valid():
            continue

        artwork.process()
        data = artwork.get_data()

        if "nodata" not in sys.argv:
            data["jsondata"] = json.dumps(data)
            data["xmldata"] = escape(etree.tostring(record))

        html = template.render(data).strip().encode('utf-8')
        yield (html, data)

if __name__ == "__main__":
    dataset = "kb" if "kbdata" in sys.argv else "na"
    gen = genamh("./data/%s-indented.xml" % dataset)

    for index, (html, data) in enumerate(gen):
        if data["amh_id"] == sys.argv[1]:
            if "dumpjson" in sys.argv:
                print json.dumps(data, indent = 4)
            else:
                print html

            sys.exit()