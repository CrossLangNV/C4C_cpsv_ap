def clean_text(text):
    return text.strip(" \n\r\xa0\t").replace("\xa0", " ")
