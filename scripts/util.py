def insert_at(text, to_insert, pos):
    return text[:pos] + to_insert + text[pos:]

def replace_text(search, replace, text):
    for item in search:
        text = text.replace(item, replace)

    return text