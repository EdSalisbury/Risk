import json
import random
from pprint import pprint
from format_columns import *

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


def build_territory_map():
    for terr_id in territories:
        cont_id = territories[terr_id]['continent']
        if cont_id not in territory_map:
            territory_map[cont_id] = list()
        territory_map[cont_id].append(terr_id)


def territory_check():
    for territory in territories:
        if not territory:
            continue

        for adj in adjacencies[territory['id']]:
            print "%s is adjacent to %s" % (
                territory['name'], territories[adj]['name'])
            if territory['id'] not in adjacencies[territories[adj]['id']]:
                print "FAIL"


def move_list(state, player_id, min):
    moves = list()
    for terr_id in state['players'][player_id]['territories']:
        for adj_terr_id in adjacencies[terr_id]:
            if adj_terr_id not in state['players'][player_id]['territories']:
                attackers = state['troops'][terr_id]
                defenders = state['troops'][adj_terr_id]
                chance = win_chance[attackers][defenders]
                if chance >= min:
                    moves.append(terr_id, adj_terr_id)
    return moves


def update_exposure(state):
    for player_id in range(0, len(state['players'])):
        for terr_id in state['players'][player_id]['territories']:
            enemy_troops = 0
            for adj_terr_id in adjacencies[terr_id]:
                if adj_terr_id not in state['players'][player_id]['territories']:
                    enemy_troops += state['troops'][adj_terr_id]
            state['exposure'][terr_id] = enemy_troops - state['troops'][terr_id]


def update_score(state):
    for player_id in range(0, len(state['players'])):
        state['players'][player_id]['score'] = 0
        for continent in state['players'][player_id]['continents']:
            state['players'][player_id]['score'] += continents[continent]['value'] * 50

        for territory in state['players'][player_id]['territories']:
            state['players'][player_id]['score'] += territories[territory]['value'] * 5
            state['players'][player_id]['score'] -= state['exposure'][territory]


def update_continents(state):
    for player_id in range(0, len(state['players'])):
        for cont_id in territory_map:
            owned = True
            for terr_id in territory_map[cont_id]:
                if terr_id not in state['players'][player_id]['territories']:
                    owned = False
            if owned:
                state['players'][player_id]['continents'].append(cont_id)


def update_troops(state, player_id):
    num_territories = len(state['players'][player_id]['territories'])
    state['players'][player_id]['troops'] += num_territories / 3
    for cont_id in state['players'][player_id]['continents']:
        state['players'][player_id]['troops'] += continents[cont_id]['value']


def init_game(profile_list):
    global state
    state['players'] = list()
    state['troops'] = [0] * (len(territories) + 1)
    state['exposure'] = [0] * (len(territories) + 1)

    num_players = len(profile_list)
    troops_per_player = rules['troops_per_player'][num_players]

    # Get list of player names
    chosen_names = list()
    for __ in range(0, len(profile_list)):
        chosen = False
        while not chosen:
            name = random.choice(names)
            if name not in chosen_names:
                chosen_names.append(name)
                chosen = True

    player_id = 0
    for profile in profile_list:
        name = chosen_names.pop()
        player = {'name': name, 'profile': profile}
        players.append(player)
        state['players'].append(dict())
        state['players'][player_id] = {'troops': troops_per_player,
                                       'territories': [],
                                       'continents': [],
                                       'score':0}
        player_id += 1


def choose_territories(state):
    territories_left = list()
    for terr_id in territories:
        territories_left.append(terr_id)
    random.shuffle(territories_left)

    player_id = 0
    for i in range(0, len(territories_left)):
        terr_id = territories_left[i]
        if state['players'][player_id]['troops'] > 0:
            state['players'][player_id]['territories'].append(terr_id)
            state['players'][player_id]['troops'] -= 1
            state['troops'][terr_id] += 1
        player_id += 1
        if player_id >= len(players):
            player_id = 0


def distribute_troops(state, player_id, initial=False):
    # Go through exposure ratings, and add troops evenly until every owned territory is 0 or less
    # With remaining troops, go through all adjacent territories, and find the one that is most valuable
    # Place all remaining troops on the owned adjacent territory
    done = False
    while state['players'][player_id]['troops'] > 0 and not done:
        max_exposure = 0
        for terr_id in state['players'][player_id]['territories']:
            if state['exposure'][terr_id] > max_exposure:
                max_exposure = state['exposure'][terr_id]
                terr_to_fortify = terr_id

        if max_exposure == 0:
            done = True
        else:
            state['troops'][terr_to_fortify] += 1
            state['players'][player_id]['troops'] -= 1
            update_exposure(state)
            if initial:
                done = True



def print_state(state):
    output = list()
    columns = list()
    for player_id, player in enumerate(state['players']):
        data = ''
        profile_name = profiles[players[player_id]['profile']]['name']
        data += "%s (%s)\n" % (players[player_id]['name'], profile_name)
        data += "Territories (%d):\n" % len(state['players'][player_id]['territories'])
        for terr_id in state['players'][player_id]['territories']:
            data += "%s (%d)\n" % (territories[terr_id]['name'], state['troops'][terr_id])
        data += "Continents (%d):\n" % len(state['players'][player_id]['continents'])
        for cont_id in state['players'][player_id]['continents']:
            data += "%s\n" % continents[cont_id]['name']
        data += "Free Troops: %d\n" % state['players'][player_id]['troops']
        data += "Score: %d\n" % state['players'][player_id]['score']
        output.append(data)
        columns.append((30, LEFT))

    print FormatColumns(columns, output)


random.seed()

territory_map = dict()
continents = load_json_data('continents')
territories = load_json_data('territories')
adjacencies = load_graph_data('adjacencies')
win_chance = load_data('probabilities')
names = load_data('names')
rules = load_data('rules')
build_territory_map()
profiles = load_data('profiles')
state = dict()
players = list()

init_game([2, 2])

choose_territories(state)

update_continents(state)
update_exposure(state)

for player_id in range(0, len(players)):
    update_troops(state, player_id)

players_to_place = list()
for player_id in range(0, len(players)):
    players_to_place.append(player_id)

while len(players_to_place) > 0:
    for player_id in players_to_place:
        if state['players'][player_id]['troops'] > 0:
            distribute_troops(state, player_id, True)
        else:
            players_to_place.remove(player_id)

update_score(state)
print_state(state)