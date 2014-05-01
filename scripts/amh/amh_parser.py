from lxml import etree
import sys, json

class Artwork():
    categories = []
    is_voc = False
    subjects = []
    params = {}
    mapper = {
        "description" : ["description"],
        "source" : ["priref"],
        "category" : ["VOC"],
        "dimensions" : ["dimension.free", "scale"],
        "date" : ["production.date.end", "production.date.start", "production.period"],
        "image_filename" : ["reproduction.reference"],
        "author" : ["creator.role", "creator"],
        "institution" : ["current_owner"],
        "accession_number" : ["alternative_number"],
        "inscriptions" : ["inscription.creator", "inscription.content"],
        "medium" : ["material", "object_category", "technique"],
        "title" : ["title"],
        "notes" : ["association.subject"],
        "other_fields" : ["related_object.reference"]
    }

    def __init__(self, record):
        for tag in record:
            for (method, tags) in self.mapper.iteritems():
                if tag.tag in tags:
                    print "%s is a %s" % (tag.tag, method)

                    if (hasattr(self, method)):
                        fn = getattr(self, method)
                        fn(tag)
                    else:
                        print "%s is not a method in this class..." % method

    def add_param(self, name, tag):
        if tag.get('lang'):
            lang = self.get_lang(tag)
            self.params[name + "_" + lang] = tag.text
        else:
            self.params[name] = tag.text

    def institution(self, tag):
        self.add_param("institution", tag)

    def title(self, tag):
        self.add_param("title", tag)

    def description(self, tag):
        self.add_param("description", tag)

    def get_lang(self, tag):
        return 'nl' if tag.get('lang') == 'nl-NL' else 'en'

    def image_filename(self, tag):
        self.add_param("image_filename", tag.text)

    def populate_categories(self):
        if self.is_voc and "plattegrond / kaart" in self.subjects:
            self.categories.append("Maps of the Dutch East India Company")

    def category(self, tag):
        if tag.tag == "VOC":
            self.is_voc = True

def parse_as_xml(filename):
    tree = etree.parse(filename)
    root = tree.getroot()
    records = tree.findall("//record")

    for record in records:
        artwork = Artwork(record)
        print json.dumps(artwork.params, indent = 4)
        sys.exit()
