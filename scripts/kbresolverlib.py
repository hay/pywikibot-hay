import re, json, urllib

PAGE_REGEX = "mpeg21:p.*:"
PAGE_A_REGEX = "mpeg21:p.*:a.*"
URL_REGEX = "http://kranten\.kb\.nl[^ ]*"
ARTICLE_URL = "http://kranten.kb.nl/view/article/id/"
PAPER_URL = "http://kranten.kb.nl/view/paper/id/"
URN_RESOLVER = "http://resolver.kb.nl/resolve?urn=%s"

def convert_paper_link(url):
    pass
    # Not ready yet, this is a bit more complicated
    # url = url.replace(PAPER_URL, "")

    # if re.search(PAGE_A_REGEX, url):


def convert_article_link(url):
    url = url.replace(ARTICLE_URL, "")

    if url.endswith(".ece"):
        url = url.replace(".ece", "")

    # The :p part of an URN is no longer used
    url = re.sub(PAGE_REGEX, "mpeg21:", url)

    return URN_RESOLVER % url

def convert_link(link):
    original_url = link.group().strip()
    url = urllib.unquote(original_url)

    if url.startswith(ARTICLE_URL):
        return (original_url, convert_article_link(url))

    # if url.startswith(PAPER_URL):
        # return (original_url, convert_paper_link(url))

    return False

def parse(text):
    links = map(convert_link, re.finditer(URL_REGEX, text))

    for link in links:
        if link:
            text = text.replace(link[0], link[1])

    return text

if __name__ == "__main__":
    f = open('./kbresolverlib.txt', 'r')
    print parse(f.read())