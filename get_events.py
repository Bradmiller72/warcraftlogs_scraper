import json
import traceback
import os
from rate_limit import get_rate_limited

api_key = os.environ.get("WARCRAFTLOGS_API_KEY")

def get_friendly_id(this_id, friendlies_id, friendlies_pet_id) -> str:
    if(this_id in friendlies_id):
        return "%s's" % friendlies_id[this_id]['name']
    elif(this_id in friendlies_pet_id):
        pet = friendlies_pet_id[this_id]['name']
        pet_owner = friendlies_pet_id[this_id]['owner']
        return "%s's pet %s" % (pet_owner, pet)
    else:
        raise Exception("Id %s was not found in friendlies or pet friendlies id dicts, type" % this_id)

def get_friendly_id_type(this_id, friendlies_id, friendlies_pet_id) -> str:
    if(this_id in friendlies_id):
        return friendlies_id[this_id]['type']
    elif(this_id in friendlies_pet_id):
        return friendlies_pet_id[this_id]['type']
    else:
        print(friendlies_id.keys())
        print(friendlies_pet_id.keys())
        raise Exception("Id %s was not found in friendlies or pet friendlies id dicts, type" % this_id)

def split_events_by_time(fight_id, fight, api_key, friendlies_id, friendlies_pet_id):
    event_time = {}
    
    start_time = fight['start_time']
    end_time = fight['end_time']

    r = get_rate_limited("https://classic.warcraftlogs.com:443/v1/report/events/debuffs/%s?translate=true&start=%s&end=%s&hostility=1&api_key=%s" % (fight_id, start_time, end_time, api_key)) #&sourceid=83

    curr_fight_info = r.json()
    
    event_time = {}
    if 'events' not in curr_fight_info:
        print(r)
        # print(r_json)
        return

    for item in curr_fight_info['events']:
        try:
            if(item['sourceIsFriendly'] == False):
                continue
            target_id = None
            if('targetID' in item):
                target_id = str(item['targetID'])
            else:
                target_id = str(item['target']['id'])

            source_id = None
            if('sourceID' in item):
                source_id = str(item['sourceID'])
            else:
                source_id = str(item['source']['id'])

            ## weird scenario where source is unknown, causing failures in fetching the id/pet id, just skipping
            # SKIPPING
            # {'timestamp': 9040247, 'type': 'removedebuff', 'source': {'name': 'Turtletongs', 'id': 294, 'guid': 7577292, 'type': 'Unknown', 'icon': 'Unknown-null'}, 'sourceIsFriendly': True, 'targetID': 297, 'targetInstance': 1, 'targetIsFriendly': False, 'ability': {'name': 'Curse of Agony', 'guid': 11712, 'type': 32, 'abilityIcon': 'spell_shadow_curseofsargeras.jpg'}}
            # SKIPPING
            # {'timestamp': 9040247, 'type': 'removedebuff', 'source': {'name': 'Turtletongs', 'id': 294, 'guid': 7577292, 'type': 'Unknown', 'icon': 'Unknown-null'}, 'sourceIsFriendly': True, 'targetID': 297, 'targetInstance': 1, 'targetIsFriendly': False, 'ability': {'name': 'Corruption', 'guid': 11671, 'type': 32, 'abilityIcon': 'spell_shadow_abominationexplosion.jpg'}}
            # SKIPPING
            # {'timestamp': 9040247, 'type': 'removedebuff', 'source': {'name': 'Turtletongs', 'id': 294, 'guid': 7577292, 'type': 'Unknown', 'icon': 'Unknown-null'}, 'sourceIsFriendly': True, 'targetID': 297, 'targetInstance': 1, 'targetIsFriendly': False, 'ability': {'name': 'Immolate', 'guid': 11667, 'type': 4, 'abilityIcon': 'spell_fire_immolation.jpg'}}
            if('source' in item and item['source']['type'] == 'Unknown'):
                print('SKIPPING')
                print(item)
                continue

            curr_key = str(item['timestamp']) + "_" + target_id

            if 'targetInstance' in item:
                curr_key += "_" + str(item['targetInstance'])

            if(curr_key not in event_time):
                event_time[curr_key] = {"removedebuff": [], "applydebuff": []}

            spell_name = item['ability']['name']
            guid = item['ability']['guid']
            curr_type = get_friendly_id_type(source_id, friendlies_id, friendlies_pet_id)

            if(item['type'] == 'applydebuff'):
                event_time[curr_key]['applydebuff'].append(
                    {
                        "spell": spell_name,
                        "id": guid,
                        "source_id": source_id,
                        "type": curr_type
                    }
                )
            elif(item['type'] == 'removedebuff'):
                event_time[curr_key]['removedebuff'].append(
                    {
                        "spell": spell_name,
                        "id": guid,
                        "source_id": source_id,
                        "type": curr_type
                    }
                )
        except:
            print(item)
            traceback.print_exc()

    key_to_delete = []
    for key, value in event_time.items():
        ## signifies the end of the fight
        if(len(value['removedebuff']) > 3):
            key_to_delete.append(key)
        ## nothing was applied, so nothing could have been replaced
        elif(len(value['applydebuff']) == 0):
            key_to_delete.append(key)
        ## nothing was replaced because nothing removed
        elif(len(value['removedebuff']) == 0):
            key_to_delete.append(key)
        ## can't find a way to match removed debuffs to applied debuffs if there is more than one, commented part is for phantom debuff, will look at later
        elif(len(value['removedebuff']) != len(value['applydebuff'])):# and (len(value['removedebuff']) != 2 or len(value['applydebuff']) != 1)):
            key_to_delete.append(key)
        elif(len(value['removedebuff']) > 1 or len(value['applydebuff']) > 1):
            key_to_delete.append(key)


    for key in key_to_delete:
        del event_time[key]

    for key, value in event_time.items():
        if(len(value['removedebuff']) != len(value['applydebuff'])):
            print(value)

    return {"fight": fight['name'], "start_time": start_time, "end_time": end_time, "id": fight['id'], "boss": fight['boss'] == 1, "events": event_time}        

def output_fight_info(event_time, start_time, end_time, friendlies_id, friendlies_pet_id, enemies_id):
    for key, value in event_time.items():
        if(len(value['removedebuff']) > 3):
            continue
        if value['removedebuff'] and value['applydebuff'] and value['removedebuff'][0]['spell'] != 'Deep Wound':
            split = key.split("_")
            time = int(split[0]) - start_time
            target_id = int(split[1])
            instance_id = None

            if(len(split) == 3):
                instance_id = int(split[2])

            if(len(value['removedebuff']) == 2 and len(value['applydebuff']) == 1):
                removed_person_1 = get_friendly_id(value['removedebuff'][0]['source_id'], friendlies_id, friendlies_pet_id)
                removed_spell_1 = value['removedebuff'][0]['spell']

                removed_person_2 = get_friendly_id(value['removedebuff'][1]['source_id'], friendlies_id, friendlies_pet_id)
                removed_spell_2 = value['removedebuff'][1]['spell']

                applied_person = get_friendly_id(value['applydebuff'][0]['source_id'], friendlies_id, friendlies_pet_id)
                applied_spell = value['applydebuff'][0]['spell']
                if(removed_spell_1 == applied_spell):
                    print("Due to Phantom Remove Debuff At time {:,} {} {}  was removed because {} {} was overwitten by {} {} on {} {}".format(time, removed_person_2, removed_spell_2, removed_person_1, removed_spell_1, applied_person, applied_spell, enemies_id[target_id], instance_id))
                elif(removed_spell_2 == applied_spell):
                    print("Due to Phantom Remove Debuff At time {:,} {} {}  was removed because {} {} was overwitten by {} {} on {} {}".format(time, removed_person_1, removed_spell_1, removed_person_2, removed_spell_2, applied_person, applied_spell, enemies_id[target_id], instance_id))
                else:
                    print(value)
                    print("Error, found two remove debuff and one apply debuff, but neither matched.")
                continue
                
            for num in range(0, len(value['removedebuff'])):
                if num >= len(value['applydebuff']):
                    continue
                removed_person = get_friendly_id(value['removedebuff'][num]['source_id'], friendlies_id, friendlies_pet_id)
                removed_spell = value['removedebuff'][num]['spell']

                applied_person = get_friendly_id(value['applydebuff'][num]['source_id'], friendlies_id, friendlies_pet_id)
                applied_spell = value['applydebuff'][num]['spell']

                if(instance_id != None):
                    print("At time {:,} {} {} was removed by {} {} on {} {}".format(time, removed_person, removed_spell, applied_person, applied_spell, enemies_id[target_id], instance_id))
                else:
                    print("At time {:,} {} {} was removed by {} {} on {}".format(time, removed_person, removed_spell, applied_person, applied_spell, enemies_id[target_id]))

if __name__ == "__main__":

    ## Change these:
    fight_id = "FmvDg9LYyKhx8HMn"
    boss_only = True



    r = get_rate_limited("https://classic.warcraftlogs.com:443/v1/report/fights/%s?translate=true&api_key=%s" % (fight_id, api_key))
    # print(r)
    r_json = r.json()
    # print(r_json)
    friendlies_id = {}
    enemies_id = {}
    friendlies_pet_id = {}


    for i in r_json['enemies']:
        enemies_id[i['id']] = i['name']

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

    all_events = {}
    for fight in r_json['fights']:
        if(fight['boss'] == 0 and boss_only):
            continue
        split_event = split_events_by_time(fight_id, fight, api_key, friendlies_id, friendlies_pet_id)
        all_events[split_event['id']] = split_event
        
    for key, value in all_events.items():
        print("Fight: %s" % value['fight'])
        output_fight_info(value['events'], value['start_time'], value['end_time'], friendlies_id, friendlies_pet_id, enemies_id)
        print()

    # print(json.dumps(all_events, indent=4))



    # print(event_time)
    