from get_events import split_events_by_time, generate_id_dicts, get_fight_events, get_fight_events_local
import requests
import json
import traceback
from bs4 import BeautifulSoup
from datetime import datetime
import os
from rate_limit import get_rate_limited
from wowhead_translations import translate

api_key = os.environ.get("WARCRAFTLOGS_API_KEY")
run_local_data = os.environ.get("RUN_LOCAL_DATA", False)

def increment_removed_list(removed_list, removed, applied):
    applied_spell_name, applied_spell_duration = translate(applied)
    removed_spell_name, removed_spell_duration = translate(removed)

    if(removed_spell_name not in removed_list):
        removed_list[removed_spell_name] = {}

    if(applied_spell_name not in removed_list[removed_spell_name]):
        removed_list[removed_spell_name][applied_spell_name] = 0

    
    removed_list[removed_spell_name][applied_spell_name] += 1

    return removed_list

def start_run(raid_ids):
    start = datetime.now()

    removed_list = {}

    for raid_id in raid_ids:
        if(raid_id == ""):
            continue

        print("Starting raid id: %s" % raid_id)

        if(run_local_data):
            events, enemies_id, friendlies_id, friendlies_pet_id = get_fight_events_local(raid_id)
        else:
            events, enemies_id, friendlies_id, friendlies_pet_id = get_fight_events(raid_id)
        for key, value in events.items():
            for key1, value1 in value['events'].items():
                removed_list = increment_removed_list(removed_list, value1['removedebuff'][0], value1['applydebuff'][0])

    print(json.dumps(removed_list, indent=4))

    end = datetime.now()
    print("Start: %s" % start)
    print("End: %s" % end)

if __name__ == "__main__":
    if(run_local_data):
        raid_ids = os.listdir("data")
        start_run(raid_ids)
    else:
        raid_ids = []
        with open('raid_list.txt', 'r') as f:
            raid_ids = f.read().split("\n")

        start_run(raid_ids)