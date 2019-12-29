import os 
import traceback
from rate_limit import get_rate_limited
from get_events import split_events_by_time, generate_id_dicts, get_fight_events
import json

api_key = os.environ.get("WARCRAFTLOGS_API_KEY")

raid_ids = []
with open('test_list.txt', 'r') as f:
    raid_ids = f.read().split("\n")

raid_directory = "data/{}"
enemies_file = raid_directory + "/enemies_id.json"
friendlies_file = raid_directory + "/friendlies_id.json"
friendlies_pet_file = raid_directory + "/friendlies_pet_id.json"
event_directory = raid_directory + "/fights"
event_file = event_directory + "/{}.json"

for raid_id in raid_ids:
    print(raid_id)
    if(raid_id == ""):
        continue

    if not os.path.exists(raid_directory.format(raid_id)):
        os.makedirs(raid_directory.format(raid_id))

    if not os.path.exists(event_directory.format(raid_id)):
        os.makedirs(event_directory.format(raid_id))

    r = get_rate_limited("https://classic.warcraftlogs.com:443/v1/report/fights/%s?translate=true&api_key=%s" % (raid_id, api_key))

    if(r.status_code != 200):
        print(r.status_code)
        print(r.json())
        continue

    r_json = r.json()

    enemies_id, friendlies_id, friendlies_pet_id = generate_id_dicts(r_json)

    with open(enemies_file.format(raid_id), 'w') as f:
        f.write(json.dumps(enemies_id))

    with open(friendlies_file.format(raid_id), 'w') as f:
        f.write(json.dumps(friendlies_id))

    with open(friendlies_pet_file.format(raid_id), 'w') as f:
        f.write(json.dumps(friendlies_pet_id))

    events = {}
    try:
        for fight in r_json['fights']:
            
            event_time = {}
    
            start_time = fight['start_time']
            end_time = fight['end_time']
            boss = fight['boss']
            fight_id = fight['id']
            name = fight['name']

            r = get_rate_limited("https://classic.warcraftlogs.com:443/v1/report/events/debuffs/%s?translate=true&start=%s&end=%s&hostility=1&api_key=%s" % (raid_id, start_time, end_time, api_key)) #&sourceid=83

            curr_fight_info = r.json()
            
            event_time = {}
            if 'events' not in curr_fight_info:
                print(r)
                # print(r_json)
                continue

            file_name = "{}_{}_{}_{}_{}".format(str(start_time), str(end_time), str(boss), str(fight_id), str(name))
            print(event_file.format(raid_id, file_name))
            with open(event_file.format(raid_id, file_name), 'w') as f:
                f.write(json.dumps(curr_fight_info))


    except:
        print(r_json.keys())
        traceback.print_exc()