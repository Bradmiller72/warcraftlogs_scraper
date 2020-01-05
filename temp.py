import os
import json

events_list = []

for report_id in os.listdir('data'):
    curr_file_directory = 'data/{}/fights'.format(report_id)
    for fight in os.listdir(curr_file_directory):
        curr_fight_file = curr_file_directory + "/{}".format(fight)

        curr_json_file = None
        with open(curr_fight_file, 'r') as f:
            curr_json_file = json.load(f)

        # print(curr_json_file)
        for event in curr_json_file['events']:
            if(event['type'] not in events_list):
                events_list.append(event['type'])

print(events_list)