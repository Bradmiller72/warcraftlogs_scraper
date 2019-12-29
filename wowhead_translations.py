import requests
from bs4 import BeautifulSoup

wowhead_spell_url = "https://classic.wowhead.com/spell=%s"

guid_table = {}
with open("translations.txt") as myfile:
    for line in myfile:
        name, var = line.partition("=")[::2]
        guid_table[name.strip()] = var.strip()

def translate(guid):
    global guid_table

    class_type = guid['type']
    guid = str(guid['id'])

    if(guid not in guid_table):
        r = requests.get(wowhead_spell_url % guid)
        soup = BeautifulSoup(r.content.decode('utf-8'), "html.parser")
        translated_guid = soup.select('h1.heading-size-1')[0].text.strip()

        if translated_guid == "Shadow Vulnerability" and class_type == "Warlock":
            translated_guid = translated_guid + " (ISB)"
        with open("translations.txt", "a") as myfile:
            myfile.write("%s=%s\n" % (guid, translated_guid))
        guid_table[guid] = translated_guid
        return translated_guid
    else:
        return guid_table[guid]