# Paddle Utils
_Python scripts for data-driven paddle tennis captains and club pros_
- tsrate: calculate TrueSkill ratings for players based on APTA league results
- detail2export: convert an APTA "detail" report into an "export" report
suitable for use with tsrate

## Background
Paddle tennis is an increasingly popular sport, with 
[APTA](http://www.platformtennis.org/) sponsored leagues established in many 
metropolitan areas in the US. The APTA has developed a player rating system 
similar to the  
[NTRP](http://s3.amazonaws.com/ustaassets/assets/1/usta_import/usta/dps/doc_13_7372.pdf) 
used in tennis, but this only goes so far in helping to answer the sorts of
questions that team captains, club pros, and club paddle chairs often find 
themselves facing:
- who should play on court 1, court 2, etc?
- who should move up (or down) a series?
- in social play, how do you pair players to create an even playing field?
- how do you properly seed teams in a tournament?

There are other player assesment tools (notably the [Gillespie 
scale](http://www.platformtennis.org/news/InstructionHealth/Gillespie-Scale.htm)),
but ultimately you end up relying on the "eye test" or some other subjective
measure of a player's ability. The growing ranks of players makes it
unlikely that the evaluator either knows what to look for, or has watched
the player enough to make an accurate assesment.

Some evaluators have started augmenting the subjective methods with some
rudimentary analysis of match results to help with these decisions. The challenge
that you run into almost immediately is how to deal with the wide range of
player ability that exists even within a single series. How much tougher is it
to win a match playing court 1, than it is playing court 2, 3, or 4? The easy
solution to this problem is to try and price the courts. Creating an arbitrary
weighting typically leads to self-fulfilling prophecies as the court 4 player's
wins are discounted, making them appear unready to play up. Deriving a weighting
scheme from the match data itself is a challenge because of variance from club
to club and year to year.

The tsrate script takes a different approach, leveraging Microsoft's
[TrueSkill](http://research.microsoft.com/en-us/projects/trueskill) algorithm.
Developed by Microsoft Research, the algorithm is used by Xbox Live games to
try and match players with others at the same skill level. TrueSkill uses
Bayesian inference to create a Gaussian belief distribution for each player
based on the outcome of games. Notably, the algorithm supports both one-vs-one
and team-based games. Heungsub Lee created an excellent implementation of
TrueSkill in python ([trueskill.org](http://trueskill.org/))

In tsrate, each set is treated as a game, and sets that go to tiebreak are counted
as draws. At some level, it doesn't make a huge difference whether to rate players
based on games, sets, or matches as there is a mathematical relationship between
them (see: [Tennis Statistics](http://robert-farrenkopf.info/tennis/tennis.htm_)
by Robert Farrenkopf) All three approaches were tested and while the outcomes were
similar, using sets as the unit of scoring yields what feels like a reasonable sigma
for the rating distribution based on the number of matches in a season. 

What you do with the calculated ratings is ultimately up to you, but I would recommend
treating it as another data point and pairing it with other methods of evaluation.


## Installation
Download ZIP of this project, and unpack into a directory. From a terminal
window, cd to that folder and run:

`pip install -r requirements.txt`

NOTE: The scripts require [Python](https://www.python.org) 2.6 or
later. Windows users will need to install the interpreter first, if they
haven't already done so. Mac and Linux users should be able to use the
version that was pre-installed with their operating system.

## Basic Usage
To rate the players within an APTA paddle series, you first need a match
export file. These can be generated on the myapta.org website using the
reporting functionality. Filter the report to a single series, clear the
club filter and apply. Download the report using the CSV link at the bottom
of the page. This should give you a file called 'matches-export.csv'.

The simplest usage of tsrate is:

`python tsrate.py matches-export.csv`

This will generate a 'ratings.csv' file with the TrueSkill rating and sigma
for every player in the series.

To display the results for a single club in the console:

`python tsrate.py matches-export.csv --display <club name>`

Last, but not least, to import initial ratings for some or all of the players:

`python tsrate.py matches-export.csv --init <player ratings file>`

Since match exports for prior years are impossible to obtain from the APTA
site, you may be interested in using the detail report that's found in the
'documents' tab of the page for your series. Download the xslx file and save
as a csv.

`python detail2export.py <csv version of detail report> --series <series>`
