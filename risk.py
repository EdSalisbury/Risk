import json
import random
cfg_dir = 'cfg'


def load_json_data(filename):
    with open('cfg/%s.json' % filename) as data_file:
        items = json.load(data_file)

    # Pre-allocate space for all of the items
    data = [None] * (len(items) + 1)
    for item in items:
        data[item['id']] = item
    return data


def load_graph_data(filename, size):
    # Pre-allocate space for all of the items
    data = [None] * size

    with open('cfg/%s.json' % filename) as data_file:
        items = json.load(data_file)

    for (src, dest) in items:
        if not data[src]:
            data[src] = list()
        if dest not in data[src]:
            data[src].append(dest)

    return data


def territory_check():
    for territory in territories:
        if not territory:
            continue

        for adj in adjacencies[territory['id']]:
            print "%s is adjacent to %s" % (territory['name'], territories[adj]['name'])
            if territory['id'] not in adjacencies[territories[adj]['id']]:
                print "FAIL"

random.seed()

continents = load_json_data('continents')
territories = load_json_data('territories')
adjacencies = load_graph_data('adjacencies', len(territories))

num_players = 2

territories_owned = list()
for i in range(0, num_players):
    territories_owned.append(list())

territories_left = list()
for territory in territories:
    if not territory:
        continue
    territories_left.append(territory['id'])
random.shuffle(territories_left)

for i in range(0, len(territories_left)):
    territories_owned[i % num_players].append(territories_left[i])





