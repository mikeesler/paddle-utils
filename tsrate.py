# Copyright 2017 Mike Esler. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
tsrate application

This is a utility for calculating the TrueSkill ratings for a set
platform tennis (aka paddle tennis) players within a league, based on
their match results.
"""


import argparse, collections, csv, datetime, operator, sys, tabulate, trueskill


def init_players(filename):
    """Load a set of initial player ratings from a ratings CSV file"""
    players = {}

    with open(filename, 'rb') as datafile:
        datareader = csv.DictReader(datafile, delimiter=',')
        for player in datareader:
            player['trueskill'] = trueskill.Rating(mu=float(player['rating']), 
                                                   sigma=float(player['sigma']))
            players[player['name']] = player

    return players



def load_export(filename, players=None):
    """Load a set of matches from an export CSV file"""
    if players is None:
        players = {}

    matches = []
    with open(filename, 'rb') as datafile:
        datareader = csv.DictReader(datafile, delimiter=',')
        for row in datareader:
            # Players name "Anonymous" indicate a forfeit, so skip
            if 'Anonymous' not in str(row):
                # Create a sortable datetime for after we dedupe
                row['Datetime'] = datetime.datetime.strptime(
                                  row['Match: Match date'], "%m/%d/%Y - %H:%M")
                matches.append(row)

                # initialize any heretofore unseen players with a default rating
                for player in (row['Home Player 1'], row['Home Player 2']):
                    if player not in players:
                        club = row['Details'].split('|')[0].split(':')[0]
                        players[player] = {'club': club, 'name': player, 
                                           'trueskill': trueskill.Rating()}
                for player in (row['Away Player 1'], row['Away Player 2']):
                    if player not in players:
                        club = row['Details'].split('|')[1].split(':')[0]
                        players[player] = {'club': club, 'name': player, 
                                           'trueskill': trueskill.Rating()}

    # APTA exports tyically contain duplicated rows, so dedupe then sort
    matches = [dict(t) for t in set(tuple(m.items()) for m in matches)]
    matches.sort(key=operator.itemgetter('Datetime'))

    return matches, players



def rate_players(matches, players):
    """Calculate the TrueSkill ratings"""
    for match in matches:
        home_team = (players[match['Home Player 1']]['trueskill'], 
                     players[match['Home Player 2']]['trueskill'])
        away_team = (players[match['Away Player 1']]['trueskill'], 
                     players[match['Away Player 2']]['trueskill'])

        home_games_won = map(int, (match['Home Set 1'], match['Home Set 2'], 
                                   match['Home Set 3']))
        away_games_won = map(int, (match['Away Set 1'], match['Away Set 2'], 
                                   match['Away Set 3']))

        # we rate the pairs based on set outcome, not individual games
        for home_score, away_score in zip(home_games_won, away_games_won):
            # if the set went to tiebreak, count it as a draw
            if (home_score + away_score) == 13:
                home_team, away_team = trueskill.rate((home_team, away_team), 
                                                      ranks=[0,0])
            elif home_score > away_score:
                home_team, away_team = trueskill.rate((home_team, away_team))
            elif home_score < away_score:
                away_team, home_team = trueskill.rate((away_team, home_team))

        players[match['Home Player 1']]['trueskill'] = home_team[0]
        players[match['Home Player 2']]['trueskill'] = home_team[1]
        players[match['Away Player 1']]['trueskill'] = away_team[0]
        players[match['Away Player 2']]['trueskill'] = away_team[1]

    # pull the mu and sigma out into their own keys for convenience
    for player in players:
        players[player]['rating'] = players[player]['trueskill'].mu
        players[player]['sigma'] = players[player]['trueskill'].sigma

    return sorted(players.values(), key=lambda x: (x['club'], -x['rating']))



def write_csv(players, outfile):
    """Write the ratings to a CSV file"""
    with open(outfile, 'w') as csvfile:
        fieldnames = ['club', 'name', 'rating', 'sigma' ]
        writer = csv.writer(csvfile)

        writer.writerow(fieldnames)
        for player in players:
            writer.writerow([player['club'], player['name'], player['rating'], 
                             player['sigma']])



def print_table(players, club):
    """Pretty print a ratings table for a single club"""
    table_data = []
    for player in players:
        if player['club'] == club:
            # use an OrderedDict to ensure the order the columns print
            row = collections.OrderedDict([
                    ('Name', player['name']), ('Rating', player['rating']), 
                    ('Sigma', player['sigma'])
                  ])
            table_data.append(row)

    print tabulate.tabulate(table_data, headers="keys")



def main(argv):
    parser = argparse.ArgumentParser(description='Calculate TrueSkill ranking of an APTA league.')
    parser.add_argument('datafile',
                        help='myapta.org formatted match export CSV file')
    parser.add_argument('resultsfile', 
                        help='output file for calculated ratings', 
                        default='ratings.csv', nargs='?')
    parser.add_argument("-i", "--init", 
                        help="CSV file of initial player ratings and sigmas", 
                        metavar="FILE")
    parser.add_argument("-d", "--display", 
                        help="show results for a single club on the console", 
                        metavar="CLUB")
    parser.add_argument("-v", "--verbose", 
                        help="show diagnostic messages on the console", 
                        action="store_true")
    args = parser.parse_args()

    players = {}
    if args.init:
        players = init_players(args.init)
        if args.verbose:
            print "Imported {} players from {}".format(len(players), args.init)

    matches, players = load_export(args.datafile, players)
    if args.verbose:
        print "Imported {} matches and {} players from {}".format(len(matches),
                                                                  len(players),
                                                                  args.datafile)

    results = rate_players(matches, players)
    if args.verbose:
        print "Rating completed"

    if args.display:
        print_table(results, args.display)
    else:
        write_csv(results, args.resultsfile)
        if args.verbose:
            print "Wrote {} records to {}".format(len(results), 
                                                  args.resultsfile)



if __name__ == "__main__":
    main(sys.argv)

