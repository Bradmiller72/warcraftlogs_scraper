# Warcraft Logs Scraper
This is a work in progress.

You need python3 to run this, I'm currently using 3.6.

## Requirements
You can pip install the requirements folder.

*ratelimit: Used to enforce a rate limit on warcraft logs api. The api limits to 240 requests/2 mins. I rate limit at 220 every 2 minutes and sleep if it goes over that.
*beautifulsoup4: This is used to grab report ids and then to grab debuff names from wowhead.

## Use
You need a warcraft logs api key. You can get this by logging into their website and generating one at the bottom of the settings page. Once you have this you can set the environment variable by doing ```export WARCRAFTLOGS_API_KEY=<api_key>```.

To show all overwritten debuffs on a single report you need to go into ```get_events.py``` and change these lines:
```
fight_id = "FmvDg9LYyKhx8HMn"
boss_only = True
```
fight_id is the report id and boss_only will only output if its a boss, you can set this to false to show every fight in the report.

Then you can run:
```
python3 get_events.py
```

Output for this will look like this:
```
Fight: Majordomo Executus
At time 7,673 Còttonnouth's Mind Flay was removed by Polar's  on Flamewaker Elite 1
At time 11,315 Tookerjubs's  was removed by Còttonnouth's Mind Flay on Flamewaker Elite 1
At time 11,724 Polar's Corruption was removed by Hineko's  on Flamewaker Elite 1
At time 16,295 Wìms's  was removed by Pohner's Serpent Sting on Flamewaker Elite 1
At time 23,868 Còttonnouth's Shadow Word: Pain was removed by Polar's Curse of Recklessness on Flamewaker Elite 3
At time 24,273 Badabadaboom's Serpent Sting was removed by Còttonnouth's Mind Flay on Flamewaker Elite 3
At time 49,382 Tookerjubs's  was removed by Còttonnouth's Mind Flay on Flamewaker Healer 2
At time 49,787 Pohner's Serpent Sting was removed by Hineko's Drain Soul on Flamewaker Healer 2
```
The timestamp will match what is shown in Warcraft logs where its seconds,milliseconds. If its over 60 seconds the timestamp will show something like 100,000 which actually relates to 1:40:00 in warcraft logs.


To run a mass report on debuffs being removed you can add every report id into raid_list.txt. Currently there is 50 in there and takes about a half hour to run.

You can then run:
```
python3 run_raid_ids.py
```
which will output a large json output with all the debuffs (see data_output/50_output.json). You can then change some values in format_json_to_csv.py to format the json to a csv file (see data_output/50_output.csv).

## Running with Local Data
You can do all of the same commands above but with local data if you download it.

To download the data, enter all the raid ids you wish into ```raid_list.txt```. Once you do that run ```python3 pull_all_data.py```, which will do the long part of pulling the data and formating it for later use.

Once thats done you can set the environment variable ```RUN_LOCAL_DATA``` like this ```export RUN_LOCAL_DATA=True``` and it will allow you to run local data with any of the commands above.

*NOTE*: To run a specific fight off local data you must have downloaded it already, so double check before running ```python3 get_events.py```.

## Questions
If you have questions you can message me on discord (Zanzabarr#5554) or open an issue here.