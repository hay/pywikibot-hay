import re, parsedatetime
from cgi import escape

cal = parsedatetime.Calendar()

class Artwork():
    record = False

    is_voc = False
    is_wic = False

    MAP_SUBJECT = "chart / map / plan"

    DIMENSION_REGEX = re.compile("(.*) x (.*) (.*)")

    NA_INVENTORYNR_CLEANUP_REGEX = re.compile("flap|\(.*\)|tek.*|[a-z]")

    YEAR_REGEX = re.compile("\d.*")

    NA_SOURCE_LINK = "http://www.gahetna.nl/collectie/archief/inventaris/index/eadid/4.%s/inventarisnr/%s/level/file"

    NA_NEW_INVENTORY_NR = "NL-HaNA_4.%s_%s"

    mapper = {
        "description" : ["description"],
        "amh_id" : ["priref"],
        "category" : ["VOC", "WIC"],
        "dimensions" : ["dimension.free"],
        "image_filename" : ["reproduction.reference"],
        "institution" : ["current_owner"],
        "institution_shortcode" : ["current_owner"],
        "inscription_text" : ["inscription.content"],
        "inscription_creator" : ["inscription.creator"],
        "medium" : ["material", "object_category", "technique"],
        "title" : ["title"],
        "notes" : ["association.subject"]
    }

    def __init__(self, record = None, locations = None):
        self.record = record
        self.locations = locations
        self.params = { "authors" : [] }
        self.subjects_nl = []
        self.subjects_en = []
        self.categories = []

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
        self.populate_authors()
        self.populate_locations()
        self.populate_company_type()
        self.populate_source_link()

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

    def populate_source_link(self):
        # For now, we can only create source links for NA files
        if self.params["institution"] != "Nationaal Archief":
            return

        ref = self.record.find("alternative_number").text

        if not ref.startswith("VEL"):
            return

        (zut, col, nr) = re.split("(VELH?)", ref)

        # Clean up the inventorynr
        nr = nr.lstrip("0").replace('_', '.')
        nr = re.sub(self.NA_INVENTORYNR_CLEANUP_REGEX, '', nr)

        link = self.NA_SOURCE_LINK % (col, nr)
        new_inventory_nr = self.NA_NEW_INVENTORY_NR %(col, nr)

        self.add_param("source_link", link)
        self.add_param("accession_number", ref)
        self.add_param("new_accesion_number", new_inventory_nr)

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
        date_tag = self.record.xpath("production.period[@lang='en-GB']")
        ref = self.record.find("priref").text

        if not date_tag or len(date_tag) == 0:
            print "No date for ID %s thing it seems!" % ref
            return

        date = date_tag[0].text.strip()
        year = self.YEAR_REGEX.findall(date)[0].strip()
        cat = False
        tmpl = False

        if date.startswith("c"):
            tmpl = "{{other date|circa|%s}}" % year
            cat = year
        elif date.startswith("after"):
            tmpl = "{{other date|after|%s}}" % year
        elif date.isdigit():
            tmpl = year
            cat = year
        elif "-" in date and not date.count("/"):
            start, end = date.split("-")
            tmpl = "{{other date|between|%s|%s}}" % (start.strip(), end.strip())

            if int(end) - int(start) < 11:
                cat = str((int(start) / 10) * 10) + "s"
        else:
            # As a last resort, use parsedatetime
            d = cal.parse(date)

            # Only parse dates
            if d[1] == 1:
                tmpl = "%s-%s-%s" % (d[0][0], d[0][1], d[0][2])

        if tmpl:
            self.add_param("date", tmpl)

            if cat:
                self.categories.append(cat)
        else:
            print "No date for ID %s thing it seems!" % ref

    def populate_subjects(self):
        self.add_param("subjects_nl", ", ".join(self.subjects_nl))
        self.add_param("subjects_en", ", ".join(self.subjects_en))

    def normalize_name(self, name):
        """ We change the 'Last name, First name' format to 'First name Last name' """
        parts = name.split(",")
        map(lambda p:p.strip(), parts)
        parts.reverse()
        name = " ".join(parts).strip()

        return name

    def get_author_string(self, creator, lang):
        if lang in creator:
            return "%s (%s)" % (creator["name"], creator[lang])
        else:
            return creator["name"]

    def get_author_name(self, creator):
        if "anonymous" not in creator["name"].lower():
            return creator["name"]
        else:
            return False

    def populate_authors(self):
        creators = []

        for creator in self.record.xpath("creator"):
            name = self.normalize_name(creator.text)
            creators.append({ "name" : name })

        # We need to match the creator.role to the creator
        for role in self.record.xpath("creator.role"):
            index = int(role.get('occurrence')) - 1 # Occurences start at 1 :/
            lang = self.get_lang(role)
            creators[index][lang] = role.text

        # Now create the relevant data for the template
        authors_en = map(lambda c:self.get_author_string(c, "en"), creators)
        authors_nl = map(lambda c:self.get_author_string(c, "nl"), creators)

        self.params.update({
            "creators" : creators,
            "authors" : filter(None, map(self.get_author_name, creators)),
            "authors_en" : ", ".join(authors_en),
            "authors_nl" : ", ".join(authors_nl)
        })

    def populate_locations(self):
        location = self.record.find("related_object.reference")

        if location is None:
            return

        location_id = location.text

        if location_id not in self.locations:
            return

        loc = self.locations[location_id]

        self.params.update({
            "location_amh_id" : loc["amh_id"],
            "location_type" : loc["kind"]
        })

        if "lat" in loc:
            self.add_param("location_lat", loc["lat"])
            self.add_param("location_lng", loc["lng"])

        if "title" in loc:
            self.add_param("location_title", self.normalize_name(loc["title"]))


    def populate_company_type(self):
        company_type = "VOC" if self.is_voc else "WIC"
        self.add_param("company_type", company_type)

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

        if not size:
            return

        w, h, u = size[0]
        w = w.replace(",", ".")
        h = h.replace(",", ".")
        sizetmpl = "{{Size|unit=%s|width=%s|height=%s}}" % (u, w, h)
        self.add_param("dimensions", sizetmpl)
