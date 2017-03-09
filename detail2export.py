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
detail2export application

This is a utility for converting an APTA 'detail report' (which is
generated at the end of a season) into the format of an 'export report'
which is available via the APTA reports module during the season.
"""


import argparse, csv, sys


def load_detail_file(filename, series):
    """Load and parse a detail report file"""
    matches = []

    with open(filename, 'rb') as datafile:
        datareader = csv.DictReader(datafile, delimiter=',')
        for row in datareader:
            if (series is None) or (row['Series'] == series):
                # Anonymous players indicate a forfeit
                if ('Anonymous' not in str(row) and row['AwayForfeit'] == '0' 
                                                and row['HomeForfeit'] == '0'):
                    match ={}

                    match['Home Player 1'] = row['HomePlayer1']
                    match['Home Player 2'] = row['HomePlayer2']
                    match['Away Player 1'] = row['AwayPlayer1']
                    match['Away Player 2'] = row['AwayPlayer2']

                    match['Details'] = row['HomeTeam'] + ':0|' + \
                                       row['AwayTeam'] + ':0'

                    month = str(int(row['MatchDate'].split('/')[0])).zfill(2)
                    day = str(int(row['MatchDate'].split('/')[1])).zfill(2)
                    year = row['MatchDate'].split('/')[2]
                    match['Match: Match date'] = "{}/{}/20{} - 19:00".format(month, 
                                                                             day,
                                                                             year)

                    match['Home Set 1'] = 0
                    match['Home Set 2'] = 0
                    match['Home Set 3'] = 0
                    match['Away Set 1'] = 0
                    match['Away Set 2'] = 0
                    match['Away Set 3'] = 0

                    # Create some bogus set scores based on the match points.
                    # In match scoring you get 1 pt for each set you win and a
                    # bonus point for winning the match. In other words, 3 pts
                    # means you won 2 sets, 1 pt means you won 1 set, and 0 pts
                    # means you won 0 sets
                    if row['HomePoints'] == '3' and row['AwayPoints'] == '0':
                        match['Home Set 1'] = 6
                        match['Home Set 2'] = 6
                        matches.append(match)
                    elif row['HomePoints'] == '3' and row['AwayPoints'] == '1':
                        match['Home Set 1'] = 6
                        match['Home Set 3'] = 6
                        match['Away Set 2'] = 6
                        matches.append(match)
                    elif row['HomePoints'] == '0' and row['AwayPoints'] == '3':
                        match['Away Set 1'] = 6
                        match['Away Set 2'] = 6
                        matches.append(match)
                    elif row['HomePoints'] == '1' and row['AwayPoints'] == '3':
                        match['Home Set 2'] = 6
                        match['Away Set 1'] = 6
                        match['Away Set 3'] = 6
                        matches.append(match)

    return matches



def write_export_file(matches, filename):
    """Write an export formatted CSV file"""
    fieldnames=matches[0].keys()
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, 
                                extrasaction='ignore')
        writer.writeheader()
        for match in matches:
            writer.writerow(match)



def main(argv):
    parser = argparse.ArgumentParser(description='Convert an APTA league detail report to export format.')
    parser.add_argument('datafile', 
                        help='myapta.org formatted match export CSV file')
    parser.add_argument('resultsfile', help='output file', default='export.csv',
                        nargs='?')
    parser.add_argument('-s', '--series', 
                        help='limit results to a specific series')
    parser.add_argument("-v", "--verbose", 
                        help="show diagnostic messages on the console", 
                        action="store_true")
    args = parser.parse_args()

    players = {}

    matches = load_detail_file(args.datafile, args.series)
    if args.verbose:
        print "Imported {} matches from {}".format(len(matches), args.datafile)

    write_export_file(matches, args.resultsfile)
    if args.verbose:
        print "Wrote {} records to {}".format(len(matches), args.resultsfile)



if __name__ == "__main__":
    main(sys.argv)

