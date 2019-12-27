from get_events import split_events_by_time
import requests
import json
import traceback
from bs4 import BeautifulSoup
from datetime import datetime
import os
from rate_limit import get_rate_limited

api_key = os.environ.get("WARCRAFTLOGS_API_KEY")

wowhead_spell_url = "https://classic.wowhead.com/spell=%s"

raid_ids = []
with open('test_list.txt', 'r') as f:
    raid_ids = f.read().split("\n")

# translator = Translator()
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


def increment_removed_list(removed_list, removed, applied):
    applied_spell_name = translate(applied)
    removed_spell_name = translate(removed)

    if(removed_spell_name not in removed_list):
        removed_list[removed_spell_name] = {}

    if(applied_spell_name not in removed_list[removed_spell_name]):
        removed_list[removed_spell_name][applied_spell_name] = 0

    
    removed_list[removed_spell_name][applied_spell_name] += 1

    return removed_list

start = datetime.now()

print(start)

removed_list = {}

for raid_id in raid_ids:
    print("Starting raid id: %s" % raid_id)
    if(raid_id == ""):
        continue
    r = get_rate_limited("https://classic.warcraftlogs.com:443/v1/report/fights/%s?translate=true&api_key=%s" % (raid_id, api_key))

    r_json = r.json()

    friendlies_id = {}
    friendlies_pet_id = {}
    
    try:
        for i in r_json['friendlies']:
            try:
                friendlies_id[str(i['id'])] = {'name': i['name'], 'type': i['type']}
            except:
                traceback.print_exc()

        for i in r_json['friendlyPets']:
            try:
                friendlies_pet_id[str(i['id'])] = {"name": i['name'], "owner": friendlies_id[str(i['petOwner'])], "type": i['type']}
            except:
                print(i)
                # print(friendlies_id.keys())
                traceback.print_exc()
    except:
        print(r_json)
        # print(friendlies_pet_id)
        # print('here')
        traceback.print_exc()

    try:
        for fight in r_json['fights']:
            split_event = split_events_by_time(raid_id, fight, api_key, friendlies_id, friendlies_pet_id)
            for key, value in split_event['events'].items():
                if(len(value['removedebuff']) > 1 or len(value['applydebuff']) > 1):
                    print(value)
                    print("More than one in one of the two")
                    continue
                removed_list = increment_removed_list(removed_list, value['removedebuff'][0], value['applydebuff'][0])
    except:
        print(r_json)
        traceback.print_exc()



print(json.dumps(removed_list, indent=4))

end = datetime.now()
print(end)
print(start)