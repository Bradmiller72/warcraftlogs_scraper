from get_events import split_events_by_time
import requests
import json
import traceback
from bs4 import BeautifulSoup
from datetime import datetime
import os
from rate_limit import get_rate_limited
from wowhead_translations import translate

api_key = os.environ.get("WARCRAFTLOGS_API_KEY")

def increment_removed_list(removed_list, removed, applied):
    applied_spell_name = translate(applied)
    removed_spell_name = translate(removed)

    if(removed_spell_name not in removed_list):
        removed_list[removed_spell_name] = {}

    if(applied_spell_name not in removed_list[removed_spell_name]):
        removed_list[removed_spell_name][applied_spell_name] = 0

    
    removed_list[removed_spell_name][applied_spell_name] += 1

    return removed_list


def start_run(raid_ids):

    start = datetime.now()

    # print(start)

    removed_list = {}

    for raid_id in raid_ids:
        if(raid_id == ""):
            continue

        print("Starting raid id: %s" % raid_id)

        r = get_rate_limited("https://classic.warcraftlogs.com:443/v1/report/fights/%s?translate=true&api_key=%s" % (raid_id, api_key))

        r_json = r.json()

        friendlies_id = {}
        friendlies_pet_id = {}
        
        try:
            for i in r_json['friendlies']:
                try:
                    friendlies_id[str(i['id'])] = {'name': i['name'], 'type': i['type']}
                except:
                    print(i)
                    traceback.print_exc()

            for i in r_json['friendlyPets']:
                try:
                    friendlies_pet_id[str(i['id'])] = {"name": i['name'], "owner": friendlies_id[str(i['petOwner'])], "type": i['type']}
                except:
                    print(i)
                    traceback.print_exc()
        except:
            print(r_json)
            traceback.print_exc()

        try:
            for fight in r_json['fights']:
                split_event = split_events_by_time(raid_id, fight, api_key, friendlies_id, friendlies_pet_id)
                for key, value in split_event['events'].items():
                    removed_list = increment_removed_list(removed_list, value['removedebuff'][0], value['applydebuff'][0])
        except:
            print(r_json.keys())
            traceback.print_exc()



    print(json.dumps(removed_list, indent=4))

    end = datetime.now()
    print("Start: %s" % start)
    print("End: %s" % end)

if __name__ == "__main__":
    raid_ids = []
    with open('test_list.txt', 'r') as f:
        raid_ids = f.read().split("\n")

    start_run(raid_ids)