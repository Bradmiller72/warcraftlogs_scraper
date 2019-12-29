import requests
from bs4 import BeautifulSoup
import json

wowhead_spell_url = "https://classic.wowhead.com/spell=%s"

guid_table = {}
with open("wowhead_translations.json") as f:
    guid_table = json.load(f)

def translate(guid):
    global guid_table

    class_type = guid['type']
    guid = str(guid['id'])

    if(guid not in guid_table):
        return add_new_spell(guid, class_type)
    else:
        return guid_table[guid]["name"], guid_table[guid]['duration']

def add_new_spell(guid, class_type):
    r = requests.get(wowhead_spell_url % guid)
    soup = BeautifulSoup(r.content.decode('utf-8'), "html.parser")

    spell_name = get_spell_name(soup)
    duration = get_duration(soup)

    if spell_name == "Shadow Vulnerability" and class_type == "Warlock":
        spell_name = spell_name + " (ISB)"

    guid_table[guid] = {
        "name": spell_name,
        "duration": duration
    }

    with open("wowhead_translations.json", "w") as f:
        f.write(json.dumps(guid_table))
    
    return spell_name, duration

def get_spell_name(soup):
    spell_name = soup.select('h1.heading-size-1')[0].text.strip()
    return spell_name

def get_duration(soup):
    for item in soup.find_all(id='spelldetails')[0].find_all("th"):
        header = item.text
        if(header == "Duration"):
            rows = item.find_next_sibling().text
            return convert_duration(rows)

    raise Exception("Didnt find a duration for this spell.")

def convert_duration(duration):
    split_duration = duration.split(" ")
    amount = split_duration[0]
    time_frame = split_duration[1]
    if(time_frame == "minutes" or time_frame == "minute"):
        return int(amount) * 60 * 1000
    elif(time_frame == "seconds" or time_frame == "second"):
        return int(amount) * 1000
    else:
        raise Exception("This time frame doesnt calculate %s for this amount %s" % (time_frame, amount))

if __name__ == "__main__":
    temp_table = {}
    for key, value in guid_table.items():
        temp_table[key] = {"name": value['name'], "duration": value['duration']*1000}

    with open("wowhead_translations.json", "w") as f:
        f.write(json.dumps(temp_table))
