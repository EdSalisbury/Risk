#!/bin/env python

import json
import random
from pprint import pprint
from copy import deepcopy
import numpy as np
from format_columns import *
import sys

cfg_dir = 'cfg'

debug = False

if len(sys.argv) > 1:
    args = sys.argv
    args.pop(0)
    if args[0] == '-d':
        debug = True
        args.pop(0)

if len(args):
    num_players = int(args[0])
    if num_players < 2 or num_players > 6:
        print "Error: invalid number of players!"
        exit()
else:
    num_players = 2

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


def attack_list(state, player_id):
    profile_id = players[player_id]['profile']
    min_chance = profiles[profile_id]['min_chance']

    attacks = list()
    for terr_id in state['players'][player_id]['territories']:
        for adj_terr_id in adjacencies[terr_id]:
            if adj_terr_id not in state['players'][player_id]['territories']:
                num_attackers = state['troops'][terr_id]
                if num_attackers < 2:
                    continue
                num_defenders = state['troops'][adj_terr_id]
                try:
                    chance = win_chance[num_attackers][num_defenders]
                except IndexError:
                    print "Warning: Cannot determine win chance with %d attackers and %d defenders" % (num_attackers, num_defenders)
                    chance = 1

                if chance >= min_chance:
                    attacks.append([terr_id, adj_terr_id, chance])
    return attacks


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
        state['players'][player_id]['continents'] = list()
        for cont_id in territory_map:
            owned = True
            for terr_id in territory_map[cont_id]:
                if terr_id not in state['players'][player_id]['territories']:
                    owned = False
            if owned:
                state['players'][player_id]['continents'].append(cont_id)


def update_troops(state, player_id):
    num_troops = 0
    num_territories = len(state['players'][player_id]['territories'])
    num_troops += num_territories / 3

    for cont_id in state['players'][player_id]['continents']:
        num_troops += continents[cont_id]['value']

    if num_troops < 3:
        num_troops = 3

    state['players'][player_id]['troops'] += num_troops
    if debug:
        print "%s has %d troops to distribute" % (players[player_id]['name'], state['players'][player_id]['troops'])


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

    while state['players'][player_id]['troops']:
        owned_territories = state['players'][player_id]['territories']
        exposed_territories = [None] * (len(territories) + 1)
        for terr_id in owned_territories:
            exposed_territories[terr_id] = state['exposure'][terr_id]
            if debug:
                print "Exposure for %s: %d" % (territories[terr_id]['name'], state['exposure'][terr_id])

        most_exposed = np.argmax(exposed_territories)
        state['troops'][most_exposed] += 1
        state['players'][player_id]['troops'] -= 1
        if debug:
            print "%s places a troop in %s" % (players[player_id]['name'], territories[most_exposed]['name'])
        update_exposure(state)


def print_state(my_state):
    output = list()
    columns = list()
    for player_id, player in enumerate(my_state['players']):
        data = ''
        profile_name = profiles[players[player_id]['profile']]['name']
        data += "%s (%s)\n" % (players[player_id]['name'], profile_name)
        data += "Territories (%d):\n" % len(my_state['players'][player_id]['territories'])
        for terr_id in my_state['players'][player_id]['territories']:
            data += "%s (%d)\n" % (territories[terr_id]['name'], state['troops'][terr_id])
        data += "Continents (%d):\n" % len(my_state['players'][player_id]['continents'])
        for cont_id in my_state['players'][player_id]['continents']:
            data += "%s\n" % continents[cont_id]['name']
        data += "Free Troops: %d\n" % my_state['players'][player_id]['troops']
        data += "Score: %d\n" % my_state['players'][player_id]['score']
        output.append(data)
        columns.append((30, LEFT))

    print FormatColumns(columns, output)


def troops_left(attackers, defenders):
    # Simplified troop loss predictor
    # Assumes battle is won, and that there will always be at least two attacking troops left
    troops = int((attackers * 1.20) - defenders)
    if troops < 2:
        troops = 2
    return troops


def get_owner(state, terr_id):
    for player_id in range(0, len(state['players'])):
        if terr_id in state['players'][player_id]['territories']:
            return player_id


def takeover(my_state, terr_id, player_id):
    old_owner_id = get_owner(my_state, terr_id)
    my_state['players'][player_id]['territories'].append(terr_id)
    my_state['players'][old_owner_id]['territories'].remove(terr_id)

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

init_list = list()

for p in range(0, num_players):
    profile = random.choice(range(0, len(profiles)))
    init_list.append(profile)

init_game(init_list)

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

print "Initial State"
print_state(state)

turn = 1
player_id = 0
game_running = True

active_players = list()
for player_id in range(0, len(players)):
    active_players.append(player_id)

while game_running:
    if player_id not in active_players:
        player_id += 1
        if player_id >= len(players):
            player_id = 0
        continue

    print
    print "Turn %d, %s's turn" % (turn, players[player_id]['name'])

    update_troops(state, player_id)
    distribute_troops(state, player_id)
    print_state(state)

    done = False
    while not done:
        possible_attacks = attack_list(state, player_id)

        deltas = list()

        for attack in possible_attacks:
            # Make a copy of the current state
            new_state = deepcopy(state)

            terr_id = attack[0]
            adj_terr_id = attack[1]
            chance = attack[2]

            enemy_player_id = get_owner(new_state, adj_terr_id)
            score_before = new_state['players'][player_id]['score']
            enemy_score_before = new_state['players'][enemy_player_id]['score']

            attackers = new_state['troops'][terr_id]
            defenders = new_state['troops'][adj_terr_id]

            new_attackers = troops_left(attackers, defenders)

            new_state['troops'][terr_id] = 1
            new_state['troops'][adj_terr_id] = new_attackers - 1
            takeover(new_state, adj_terr_id, player_id)

            update_continents(new_state)
            update_exposure(new_state)
            update_score(new_state)

            score_after = new_state['players'][player_id]['score']
            enemy_score_after = new_state['players'][enemy_player_id]['score']

            player_delta = score_after - score_before
            enemy_delta = enemy_score_after - enemy_score_before

            delta = player_delta - enemy_delta

            deltas.append(delta)
            if debug:
                print "%s -> %s (%f) = %d/%d (%d) - %d/%d (%d) == %d" % (territories[terr_id]['name'], territories[adj_terr_id]['name'], chance,
                                             score_before, score_after, player_delta, enemy_score_before, enemy_score_after, enemy_delta, delta)

        if len(deltas):
            best_attack = np.argmax(deltas)

            # Make sure that this is a good move to make
            if max(deltas) > 0:
                attack = possible_attacks[best_attack]
                terr_id = attack[0]
                adj_terr_id = attack[1]
                enemy_player_id = get_owner(state, adj_terr_id)
                print "%s attacks %s (owned by %s) from %s." % (players[player_id]['name'], territories[adj_terr_id]['name'], players[enemy_player_id]['name'], territories[terr_id]['name'])
                attackers = state['troops'][terr_id]
                defenders = state['troops'][adj_terr_id]

                # TODO: Actual battle simulation
                new_attackers = troops_left(attackers, defenders)

                state['troops'][terr_id] = 1
                state['troops'][adj_terr_id] = new_attackers - 1
                takeover(state, adj_terr_id, player_id)

                update_continents(state)
                update_exposure(state)
                update_score(state)
            else:
                print "%s does not attack." % players[player_id]['name']
                done = True
        else:
            print "%s does not attack." % players[player_id]['name']
            done = True

    # TODO: Move Troops

    # Check to see if a player gets knocked out
    for p in active_players:
        if len(state['players'][p]['territories']) == 0:
            print "Player %s has been eliminated by %s!" % (players[p]['name'], players[player_id]['name'])
            active_players.remove(p)

    # Check to see if the player wins
    if len(active_players) == 1:
        print "%s wins!" % players[player_id]['name']
        game_running = False

    print_state(state)

    turn += 1

    player_id += 1
    if player_id >= len(players):
        player_id = 0
