""" Parse the 'locaties' xml to a simple id with lat/lng """
from lxml import etree
import sys, json, re

def load(filename, kind):
    tree = etree.parse(filename)
    records = tree.findall("//record")
    return parse_records(records, kind)

def transform(record):
    data = {
        "id" : record.find("object_number").text,
        "amh_id" : record.find("priref").text
    }

    lat = record.find("latitude").text,
    lng = record.find("longitude").text

    if lat is not "0" and lng is not "0":
        data["lat"] = lat[0]
        data["lng"] = lng

    # We just take the first title, bit unclear what actually is the correct
    # title. Also, en/nl seems to be exactly the same...
    title = record.xpath("title[@lang='en-GB'][@occurrence='1']")

    if title:
        data["title"] = title[0].text

    return data

def parse_records(records, kind):
    data = {}

    for record in records:
        info = transform(record)
        info["kind"] = kind
        ref = info["id"]

        # We only add posts that have either location or title
        if "title" in info or "lat" in info:
            data[ref] = info

    return data

def get_locations():
    posts = load("./data/locaties-indented.xml", "post")
    forts = load("./data/forten-indented.xml", "fort")
    posts.update(forts)
    return posts

if __name__ == "__main__":
    locations = get_locations()
    print json.dumps(locations, indent = 4)