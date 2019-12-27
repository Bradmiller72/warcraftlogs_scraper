import json

data = None
with open('data_output/50_output.json') as json_file:
    data = json.load(json_file)

# print(data)

with open('data_output/50_output.csv', 'w') as f:
    f.write("Debuff,Pushed Off By,Number\n")
    for key, value in data.items():
        for key1, value1 in value.items():
            f.write("%s,%s,%s\n" %(key, key1, value1))