import json
import random
from pprint import pprint

cfg_dir = 'cfg'


def load_json_data(filename):
    with open('cfg/%s.json' % filename) as data_file:
        items = json.load(data_file)

    data = dict()
    for item in items:
        data[item['id']] = item
    return data


def load_graph_data(filename):
    data = dict()

    with open('cfg/%s.json' % filename) as data_file:
        items = json.load(data_file)

    for (src, dest) in items:
        if src not in data:
            data[src] = list()
        if dest not in data[src]:
            data[src].append(dest)

    return data


def load_data(filename):
    with open('cfg/%s.json' % filename) as data_file:
        data = json.load(data_file)
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
adjacencies = load_graph_data('adjacencies')
win_chance = load_data('probabilities')
names = load_data('names')

# Build list of territories in each continent
territories_in_continents = dict()
for territory in territories:
    cont_id = territories[territory]['continent']
    if cont_id not in territories_in_continents:
        territories_in_continents[cont_id] = list()
    territories_in_continents[cont_id].append(territory)

num_players = 2

troops_per_player = 50 - (num_players * 5)

# Create players
players = list()
for i in range(0, num_players):
    player = {'id': i, 'troops': troops_per_player, 'name': random.choice(names), 'territories': list(), 'continents': list()}
    players.append(player)

# Distribute territories (Random distribution)
territories_left = list()
for territory in territories:
    territories_left.append(territory)
random.shuffle(territories_left)

for i in range(0, len(territories_left)):
    players[i % num_players]['territories'].append(territories_left[i])

troops = dict()
for territory in territories:
    troops[territory] = 0

# Distribute troops evenly
for player in players:
    player_id = player['id']
    while player['troops'] > 0:
        for terr_id in player['territories']:
            if player['troops'] == 0:
                continue

            troops[terr_id] += 1
            player['troops'] -= 1

for player in players:
    print "Player name: %s" % player['name']

    # List territories owned by a player

    print "Number of territories owned: %d" % len(player['territories'])
    print "Territories owned:"
    for territory in player['territories']:
        print territories[territory]['name']


    # See which continents are owned by a player
    for continent in territories_in_continents:
        owned = True
        for territory in territories_in_continents[continent]:
            if territory not in player['territories']:
                owned = False
        if owned:
            player['continents'].append(continent)

    print "Continents owned:"
    for continent in player['continents']:
        print continents[continent]['name']

    # Add troops for total number of owned territories
    player['troops'] += len(player['territories']) / 3

    print "Free troops: %d" % player['troops']

    print
