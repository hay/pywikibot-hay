import re
from cgi import escape

class Artwork():
    record = False

    categories = []

    is_voc = False
    is_wic = False

    subjects_nl = []
    subjects_en = []

    MAP_SUBJECT = "chart / map / plan"

    params = {}

    DIMENSION_REGEX = re.compile("(.*) x (.*) (.*)")

    YEAR_REGEX = re.compile("\d.*")

    mapper = {
        "description" : ["description"],
        "amh_id" : ["priref"],
        "category" : ["VOC", "WIC"],
        "dimensions" : ["dimension.free"],
        "image_filename" : ["reproduction.reference"],
        "author" : ["creator.role", "creator"],
        "institution" : ["current_owner"],
        "institution_shortcode" : ["current_owner"],
        "accession_number" : ["alternative_number"],
        "inscription_text" : ["inscription.content"],
        "inscription_creator" : ["inscription.creator"],
        "medium" : ["material", "object_category", "technique"],
        "title" : ["title"],
        "notes" : ["association.subject"],
        "other_fields" : ["related_object.reference"]
    }

    def __init__(self, record):
        self.record = record

    def itertags(self, record):
        for tag in record:
            for (method, tags) in self.mapper.iteritems():
                if tag.tag in tags:
                    yield (tag, method)

    def process(self):
        """
        We loop through all tags in the record. Then we go through the mapper
        and check if it's available there. If so, we then check if there's a
        method in this class with that name (for custom stuff), otherwise we
        just add the value of the tag as the value of that map key
        """
        for (tag, method) in self.itertags(self.record):
            if (hasattr(self, method)):
                fn = getattr(self, method)
                val = fn(tag)

                # If we have a return value, assign that to the property
                if val:
                    self.add_param(method, val)
            else:
                self.add_param_from_tag(method, tag)

        self.populate_categories()
        self.populate_date()
        self.populate_subjects()

    def add_param(self, name, text):
        self.params[name] = escape(text)

    def add_param_from_tag(self, name, tag):
        if tag.get('lang'):
            lang = self.get_lang(tag)
            param = name + "_" + lang
            self.add_param(param, tag.text)
        else:
            self.add_param(name, tag.text)

    def get_lang(self, tag):
        return 'nl' if tag.get('lang') == 'nl-NL' else 'en'

    def get_data(self):
        self.params["categories"] = self.categories
        return self.params

    def is_valid(self):
        """A few records we discard because they're too complex to translate to
        Commons"""

        if len(self.record.findall("current_owner")) != 1:
            print("Sorry, We need one, and only one, owner")
            return False

        return True

    def populate_categories(self):
        if self.is_voc and self.MAP_SUBJECT in self.subjects_en:
            self.categories.append("Maps of the Dutch East India Company")
        elif self.is_voc:
            self.categories.append("Dutch East India Company")
        elif self.is_wic and self.MAP_SUBJECT in self.subjects_en:
            self.categories.append("Maps of the West-Indische Compagnie")
        elif self.is_wic:
            self.categories.append("West-Indische Compagnie")

    def category(self, tag):
        if tag.tag == "VOC":
            self.is_voc = True

        if tag.tag == "WIC":
            self.is_wic = True

    def institution_shortcode(self, tag):
        if tag.text == "Koninklijke Bibliotheek":
            return "kb"
        elif tag.text == "Nationaal Archief":
            return "na"

    def populate_date(self):
        date = self.record.xpath("production.period[@lang='en-GB']")[0].text
        year = self.YEAR_REGEX.findall(date)[0]
        cat = False
        ref = self.record.find("priref").text

        if date.startswith("ca."):
            tmpl = "{{other date|circa|%s}}" % year
            cat = year
        elif date.startswith("after."):
            tmpl = "{{other date|after|%s}}" % year
        elif date.isdigit():
            tmpl = year
            cat = year
        elif "-" in date:
            start, end = date.split("-")
            tmpl = "{{other date|between|%s|%s}}" % (start, end)

            if int(end) - int(start) < 11:
                cat = str((int(start) / 10) * 10) + "s"
        else:
            print "AAARGH!!!"

        print (ref, date, cat, tmpl)

    def _populate_date(self):
        import pdb;pdb.set_trace()
        start = self.record.find("production.date.start").text
        end = self.record.find("production.date.end").text

        if start == end:
            date = start
            self.categories.append(date)
        else:
            date = "{{other date|-|%s|%s}}" % (start, end)

            if int(end) - int(start) < 11:
                cat = str((int(start) / 10) * 10) + "s"
                self.categories.append(cat)

        self.add_param("date", date)

    def populate_subjects(self):
        self.add_param("subjects_nl", ", ".join(self.subjects_nl))
        self.add_param("subjects_en", ", ".join(self.subjects_en))

    def notes(self, tag):
        lang = self.get_lang(tag)
        subjects = getattr(self, "subjects_" + lang)
        subjects.append(tag.text)

    def description(self, tag):
        # Pfff, for some reason lots of descriptions have "- " in the string
        if tag.text.startswith("- "):
            tag.text = tag.text.replace("- ", "")

        self.add_param_from_tag("description", tag)

    def dimensions(self, tag):
        size = self.DIMENSION_REGEX.findall(tag.text)
        w, h, u = size[0]
        w = w.replace(",", ".")
        h = h.replace(",", ".")
        sizetmpl = "{{Size|unit=%s|width=%s|height=%s}}" % (u, w, h)
        self.add_param("dimensions", sizetmpl)
