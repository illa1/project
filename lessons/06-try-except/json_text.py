import json

data = {
    'name': 'Illa',
    'city': 'K-P',
    'hobbies': ['reading', 'walking']
}

with open('json.txt', 'w') as file:
    json.dump(data, file)

with open('json.txt', 'r') as file:
    data_file = json.load(file)
    print(data_file)

print(data_file['name'])