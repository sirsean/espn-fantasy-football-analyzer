
"""
Represents a team in the league.
Keep track of the team's actual record and optimum record, as well as the players who scored above their average against this team.
"""
class Team:
	def __init__(self, name):
		self.name = name
		
		self.actualWins = 0
		self.actualLosses = 0
		self.actualTies = 0
		self.optimumWins = 0
		self.optimumLosses = 0
		self.optimumTies = 0

		self.actualPointsFor = 0
		self.actualPointsAgainst = 0
		self.optimumPointsFor = 0
		self.optimumPointsAgainst = 0

		self.aboveAverageOpposingPlayerPointsLines = []

		self.highScoringBenchPlayers = []
		self.lowScoringStarters = []

	"""
	Add a player points line to this team, to keep track of those players who scored above their average against this team.
	"""
	def addAboveAverageOpposingPlayerPointsLine(self, line):
		self.aboveAverageOpposingPlayerPointsLines.append(line)

		self.aboveAverageOpposingPlayerPointsLines.sort(PlayerPointsLine.sortByDifferenceFromAverage)

	"""
	Add a player points line to the high scoring bench players list.
	"""
	def addHighScoringBenchPlayerPointsLine(self, line):
		self.highScoringBenchPlayers.append(line)

		self.highScoringBenchPlayers.sort(PlayerPointsLine.sortByName)

	"""
	Add a player points line to the low scoring starters list.
	"""
	def addLowScoringStarterPlayerPointsLine(self, line):
		self.lowScoringStarters.append(line)

		self.lowScoringStarters.sort(PlayerPointsLine.sortByName)

	"""
	Get the total number of points scored against this team, over the course of the whole season, by players who scored more than their average in the game in which they faced this team.
	"""
	def getTotalOpposingPlayersPointsAboveAverage(self):
		total = 0
		for line in self.aboveAverageOpposingPlayerPointsLines:
			total += line.weekPoints - line.averagePoints
		return total

	"""
	Sorting function to help sort teams by optimum points, in descending order.
	"""
	def sortByOptimumPointsForDescending(team1, team2):
		return cmp(team2.optimumPointsFor, team1.optimumPointsFor)

	"""
	Sorting function to help sort teams by optimum wins, in descending order.
	"""
	def sortByOptimumWinsDescending(team1, team2):
		return cmp(team2.optimumWins, team1.optimumWins)

"""
Represents a single player.
This is a definitive datasource; there should only be one instance of this object per player.
Contains a list of the player's weekly scoring lines, and calculates total/average points.
"""
class Player:
	def __init__(self, playerId, name):
		self.scoreLines = []
		self.playerId = playerId
		self.name = name

		self.totalPoints = 0
		self.averagePoints = 0
		self.linesAboveAverage = []
		self.linesBelowAverage = []

	"""
	Add a PlayerScoreLine to this player's record.
	"""
	def addScoreLine(self, scoreLine):
		self.scoreLines.append(scoreLine)

	"""
	Analyze the scores for this player over the course of the season.
	Compiles the total points and the average weekly points, then calculates which games were above and below average.
	"""
	def analyzeScores(self):
		# first sum the points
		self.totalPoints = 0
		for scoreLine in self.scoreLines:
			self.totalPoints += scoreLine.points

		# calculate the average
		self.averagePoints = (self.totalPoints * 1.0) / len(self.scoreLines)

		# determine which lines are above and below average
		self.linesAboveAverage = []
		self.linesBelowAverage = []
		for scoreLine in self.scoreLines:
			if scoreLine.points > self.averagePoints:
				self.linesAboveAverage.append(PlayerPointsLine(self, scoreLine))
			elif scoreLine.points < self.averagePoints:
				self.linesBelowAverage.append(PlayerPointsLine(self, scoreLine))

	"""
	Get this player's points line for the given week.
	"""
	def getAboveAverageWeeklyPointsLine(self, week):
		for line in self.linesAboveAverage:
			if line.playerId == self.playerId and line.week == week:
				return line
		else:
			return None

"""
A simple class to represent the points a player scored in a given week, compared to their average points.
There will be many of these for each player, depending on how often they scored above/below average against various teams.
This is not a definitive data source for anything; it's created on the fly from the actual score line.
"""
class PlayerPointsLine:
	def __init__(self, player, playerScoreLine):
		self.scoreLine = playerScoreLine
		self.playerId = player.playerId
		self.name = player.name
		self.averagePoints = player.averagePoints
		self.week = playerScoreLine.week
		self.weekPoints = playerScoreLine.points

	"""
	Determine if this line represents a high scoring bench player.
	"""
	def isHighScoringBenchPlayer(self):
		return (self.scoreLine.slot == 'Bench' and self.weekPoints > 12)
		#return (self.scoreLine.slot == 'Bench' and self.weekPoints > self.averagePoints)

	"""
	Determine if this line represents a low scoring starter.
	"""
	def isLowScoringStarter(self):
		return (self.scoreLine.slot != 'Bench' and self.scoreLine.slot != 'IR' and self.weekPoints < 10)
		#return (self.scoreLine.slot != 'Bench' and self.scoreLine.slot != 'IR' and self.weekPoints < self.averagePoints)

	"""
	Sorting function to sort by the difference between the week's points and the player's average, in descending order.
	"""
	def sortByDifferenceFromAverage(lineA, lineB):
		return cmp(lineB.weekPoints - lineB.averagePoints, lineA.weekPoints - lineA.averagePoints)

	"""
	Sorting function to sort by the player's name.
	"""
	def sortByName(lineA, lineB):
		return cmp(lineA.name, lineB.name)


