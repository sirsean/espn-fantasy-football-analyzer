import re
import sys
import os
from domain.parse import GameScore, Season

"""
Get a sorted list of all the weeks in the given year's directory.
"""
def get_weeks(year, startWeek, endWeek):
	weeks = []
	for weekDirectory in os.listdir(str(year)):
		if weekDirectory[0] != '.':
			weeks.append(int(weekDirectory))
	weeks.sort()

	realWeeks = []
	for week in weeks:
		if (startWeek is None or week >= startWeek) and (endWeek is None or week <= endWeek):
			realWeeks.append(week)

	return realWeeks

"""
Get a sorted list of all the games in the given year/week directory.
"""
def get_games(year, week):
	games = []
	for game in os.listdir(os.path.join(str(year), str(week))):
		if game[0] != '.':
			games.append(int(game))
	games.sort()
	return games

"""
Parse out the command line arguments, which must include a year and may include a starting week and/or an ending week.
Also allow the user to define what they want to print, from among: gameScores, teamRecordSummary, teamPointsSummary, playerScoreSummary, teamAboveAverageOpposingPlayersSummary
"""
def parse_args(args):
	year = None
	startWeek = None
	endWeek = None
	display = []

	for arg in args:
		if not re.search('=', arg):
			continue
		[ key, value ] = arg.split('=')

		if key == '--year':
			year = int(value)
		elif key == '--startWeek':
			startWeek = int(value)
		elif key == '--endWeek':
			endWeek = int(value)
		elif key == '--display':
			display = value.split(',')
	
	if year is None:
		raise Error("Year required")

	return (year, display, startWeek, endWeek)

if __name__ == '__main__':
	try:
		(year, display, startWeek, endWeek) = parse_args(sys.argv)
	except:
		print "Usage: fantasyfootballparser.py --year=<year> [--startWeek=<startWeek> --endWeek=<endWeek>]"
		sys.exit(1)

	# determine which weeks we're going to be analysing
	weeks = get_weeks(year, startWeek, endWeek)
	season = Season(year)
	for week in weeks:
		# get the games in this week
		games = get_games(year, week)

		# parse the game score from each file
		for game in games:
			gameScore = GameScore(year, week, game)
			season.addGame(gameScore)

	if "gameScores" in display:
		print
		# print the games, and winner info
		for gameScore in season.games:
			print "Week %d, game %d, winner; actual: %s, optimum: %s" % (gameScore.week, gameScore.game, gameScore.actualWinner, gameScore.optimumWinner)

			for teamName in gameScore.teams:
				print "Week %d, game %d, %s; actual: %d, optimum: %d" % (gameScore.week, gameScore.game, teamName, gameScore.teams[teamName].actualPoints, gameScore.teams[teamName].optimumPoints)

	# perform further analysis on the season
	season.analyze()

	if "teamPointsSummary" in display:
		print
		print "Team Points Summary:"
		season.printTeamPointsSummary()

	if "teamRecordSummary" in display:
		print
		print "Team Record Summary:"
		season.printTeamRecordSummary()

	if "playerScoreSummary" in display:
		print
		print "Player Score Summary:"
		season.printPlayerScoreSummary()

	if "teamAboveAverageOpposingPlayersScoreSummary" in display:
		print
		print "Team Above Average Opposing Players Score Summary:"
		season.printTeamAboveAverageOpposingPlayersSummary()


