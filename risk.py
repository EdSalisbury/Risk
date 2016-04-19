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

for territory in territories:
    territories[territory]['troops'] = 0
    territories[territory]['owner'] = 0

# Distribute territories (Random distribution)
territories_left = list()
for territory in territories:
    territories_left.append(territory)
random.shuffle(territories_left)

for i in range(0, len(territories_left)):
    players[i % num_players]['territories'].append(territories_left[i])
    territories[territories_left[i]]['owner'] = i % num_players

# Distribute troops evenly
for player in players:
    player_id = player['id']
    while player['troops'] > 0:
        for terr_id in player['territories']:
            if player['troops'] == 0:
                continue

            territories[terr_id]['troops'] += 1
            player['troops'] -= 1

for player in players:
    print "Player name: %s" % player['name']
    score = 0.0

    # List territories owned by a player

    print "Number of territories owned: %d" % len(player['territories'])
    # print "Territories owned:"
    for territory in player['territories']:
        # print territories[territory]['name']
        score += territories[territory]['value'] * 5

    # See which continents are owned by a player
    for continent in territories_in_continents:
        owned = True
        for territory in territories_in_continents[continent]:
            if territory not in player['territories']:
                owned = False
        if owned:
            player['continents'].append(continent)


    # Add troops for continents
    print "Continents owned:"
    for continent in player['continents']:
        player['troops'] += continents[continent]['value']
        print continents[continent]['name']
        score += continents[continent]['value'] * 50


    # Add troops for total number of owned territories
    player['troops'] += len(player['territories']) / 3

    print "Free troops: %d" % player['troops']

    print "Score: %d" % score



    # Place troops
    # Placement rules:
    #
    # Territory exposure value:
    # Determine how vulnerable a territory is
    # Factors:
    #   Minimum of 2 troops on any exposed territory
    #   Calculate exposure:
    #   Go through adjacencies
    #      If adjancent territory is not owned by the player, it's exposed
    #      Add up enemy troops in adjancecies, subtract the player troops
    #   Should a territory's value come into play?
    # If not exposed, then 1 troop is fine

# Determine exposure for each territory
for territory in territories:
    enemy_troops = 0
    for adj in adjacencies[territory]:
        if territories[adj]['owner'] != territories[territory]['owner']:
            enemy_troops += territories[adj]['troops']
    territories[territory]['exposure'] = enemy_troops - territories[territory]['troops']

# Win chance threshold (TODO: make configurable)
win_chance_min = 0.7

# Determine move list
for player in players:
    print "Player: %d" % player['id']
    for territory in player['territories']:
        for adj in adjacencies[territory]:
            if territories[adj]['owner'] != player:
                attackers = territories[territory]['troops']
                defenders = territories[adj]['troops']
                chance = win_chance[attackers][defenders]
                if chance >= win_chance_min:
                    print "Attack %s from %s (%d%%)" % (territories[territory]['name'], territories[adj]['name'], chance * 100)


# Move generation:
# Go through owned territories
# Find adjacencies that are not owned by the player
# Get troop numbers for each
# Look up probabilities of winning a battle between the terrorities
# See if it's above a threshold
