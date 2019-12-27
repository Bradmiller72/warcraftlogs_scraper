import requests
from bs4 import BeautifulSoup
import re

mc_logs = "https://classic.warcraftlogs.com/zone/reports?zone=1000&page=%s"

f = open("raid_ids.txt", "w")

# i = 1
for i in range(1,50):
    r = requests.get(mc_logs % i)
    # print(r)
    soup = BeautifulSoup(r.content.decode('utf-8'), "html.parser")
    raid_id = []
    all_raid_links = soup.find_all('a', href = re.compile("/reports/"))

    for link in all_raid_links:
        groups = re.search(r"/reports/([a-zA-Z0-9]{16})", link.attrs['href'])
        f.write(groups.group(1) + "\n")

f.close()