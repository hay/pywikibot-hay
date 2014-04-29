import re, util, collections, json

LICENSE_HEADER_TEMPLATE = "{{int:license-header}}"
JUST_LICENSE_HEADER_TEMPLATE = "{{int:license}}"
LICENSE_HEADER = "=={{int:license-header}}=="
LICENSE_HEADER_SPACED = "== {{int:license-header}} =="
ARCHIVE_TEMPLATE_PAGE = "Nationaal Archief-license"
ARCHIVE_TEMPLATE = "{{%s}}" % ARCHIVE_TEMPLATE_PAGE
CAT_LINK = "[[Category:Images from Anefo]]"
LICENSE_TEMPLATE = "{{cc-by-sa-3.0-nl}}"
LICENSE_TEMPLATE_GENERIC = "{{cc-by-sa-3.0}}"
LICENSE_TEMPLATE_CAPITALIZED = "{{Cc-by-sa-3.0-nl}}"
LICENSE_TEMPLATE_SHORTENED = "{{CC-BY-SA}}"
LICENSE_HEADER_AND_TEMPLATE_NL = """
=={{int:license-header}}==
{{cc-by-sa-3.0-nl}}
"""
LICENSE_HEADER_AND_TEMPLATE = """
=={{int:license-header}}==
{{cc-by-sa-3.0}}
"""

LICENSE_HEADER_REGEX = "== ?{{int:license(?:-header)?}} ?=="
LICENSE_TEMPLATE_REGEX = re.compile("{{cc-by-sa(?:-3.0)?(?:-nl)?}}", re.IGNORECASE)
TEMPLATE_IN_INFORMATION = re.compile(
    "{{Information.*{{Nationaal Archief-license}}.*}}",
    re.MULTILINE | re.DOTALL
)

class Result:
    def __init__(self, summary = "", text = "", outputMessage = "No message", success = False):
        self.outputMessage = outputMessage
        self.success = success
        self.summary = summary
        self.text = text

def remove_cat_license(text):
    text = re.sub(LICENSE_HEADER_REGEX, "", text)
    text = re.sub(LICENSE_TEMPLATE_REGEX, "", text)
    text = text.replace(CAT_LINK, "")
    return text

def replacer(text):
    # All these conditions are mostly cleaning up stuff
    # from earlier bot runs
    if (
        ("{{Nationaal Archief-license|" in text) and
        (ARCHIVE_TEMPLATE in text)
    ):
        text = text.replace("{{Nationaal Archief-license}}", "")

        return Result(
            outputMessage = "Two NA-licenses in this file, removing the extra one",
            success = True,
            summary = "Robot: removing double Nationaal Archief-license templates",
            text = text
        )
    elif text.count(ARCHIVE_TEMPLATE_PAGE) > 1:
        text = ''.join(text.rsplit(ARCHIVE_TEMPLATE, 1))

        return Result(
            outputMessage = "More than one NA-license, removing the 'lower' one",
            summary = "Robot: removing double Nationaal Archief-license templates",
            success = True,
            text = text
        )
    elif (ARCHIVE_TEMPLATE in text and
         not re.search(LICENSE_HEADER_REGEX ,text) and
         re.search(TEMPLATE_IN_INFORMATION, text)):
        return Result(
            outputMessage = "Archive template is in an information box, so no license header needed",
            success = False
        )
    elif (
            (ARCHIVE_TEMPLATE in text) and
            (LICENSE_HEADER_TEMPLATE not in text) and
            (JUST_LICENSE_HEADER_TEMPLATE not in text)
        ):

        text = text.replace(
            ARCHIVE_TEMPLATE,
            LICENSE_HEADER_SPACED + "\n" + ARCHIVE_TEMPLATE
        )

        return Result(
            outputMessage = "This file has a NA-license, but no license header, re-adding",
            summary = "Robot: re-adding the license header",
            success = True,
            text = text
        )
    elif (ARCHIVE_TEMPLATE_PAGE in text) and (
            (LICENSE_HEADER_AND_TEMPLATE in text) or
            (LICENSE_HEADER_AND_TEMPLATE_NL in text)
        ):

        text = remove_cat_license(text)

        return Result(
            outputMessage = "This file seems to have a remaining CC-BY-SA license AND header",
            summary = "Robot: removing redundant CC-license, this is already transcluded in the template",
            success = True,
            text = text
        )
    elif (ARCHIVE_TEMPLATE_PAGE in text) and (
            (LICENSE_TEMPLATE_CAPITALIZED in text) or
            (LICENSE_TEMPLATE in text)
        ):
        # Only remove the license
        text = remove_cat_license(text)

        return Result(
            outputMessage = "This file seems to have a remaining CC-BY-SA license",
            summary = "Robot: removing redundant CC-license, this is already transcluded in the template",
            success = True,
            text = text
        )
    elif (ARCHIVE_TEMPLATE in text and
            (
                (LICENSE_HEADER_SPACED in text) or
                (LICENSE_HEADER in text)
            )
        ) and (
            (
                text.find(LICENSE_HEADER_SPACED) > text.find(ARCHIVE_TEMPLATE)
            ) or (
                text.find(LICENSE_HEADER) > text.find(ARCHIVE_TEMPLATE)
            )
        ):

        # There's a license header, but it's lower than the template tag
        text = util.replace_text(
                (LICENSE_HEADER, LICENSE_HEADER_SPACED),
                "", text
        ).replace(
            ARCHIVE_TEMPLATE,
            LICENSE_HEADER_SPACED + "\n" + ARCHIVE_TEMPLATE + "\n"
        )

        return Result(
            outputMessage = "Replacing the license header more to the top",
            summary = "Robot: fixing the license header tag",
            success = True,
            text = text
        )
    elif (ARCHIVE_TEMPLATE_PAGE in text) and (len(re.findall(LICENSE_HEADER_REGEX, text))) > 1:
        # Double license headers, removing them both and TRY BETTER
        to_insert = "%s\n%s\n" % (LICENSE_HEADER_SPACED, ARCHIVE_TEMPLATE)
        text = re.sub(LICENSE_HEADER_REGEX, "", text)
        text = text.replace(ARCHIVE_TEMPLATE, to_insert)

        return Result(
            outputMessage = "Double license headers, removing them both and adding one above the license template",
            success = True,
            summary = "Robot: removing double license headers",
            text = text
        )
    elif ARCHIVE_TEMPLATE_PAGE in text:
        return Result(
            outputMessage = "This page already has an archive template, skipping",
            success = False
        )
    # From here it's 'untreated' files
    elif "{{Information" in text:
        # No license header, add it at the end of the Information box

        text = remove_cat_license(text)

        # Find the first occurence of a category and add it before that
        pos = text.find("[[Category:")
        text = util.insert_at(text, LICENSE_HEADER_SPACED + "\n" + ARCHIVE_TEMPLATE + "\n", pos)

        return Result(
            outputMessage = "Found an information template",
            summary = "Robot: Adding a Nationaal Archief license template, then removing the manual added category",
            success = True,
            text = text
        )
    else:
        return Result(
            outputMessage = "Nothing found to replace",
            success = False
        )

def anefo_replacer(text):
    return replacer(text)

if __name__ == "__main__":
    f = open("nalib.txt", "r")
    r = anefo_replacer(f.read())
    print json.dumps(r.__dict__, indent = 4)
    print r.text