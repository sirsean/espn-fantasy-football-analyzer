import re
from domain.analysis import Team, Player, PlayerPointsLine

"""
Represent a fantasy football season.
Contains all the games played during the season, all the teams involved,
and all the players who spent any time on the roster.
"""
class Season:
	def __init__(self, year):
		self.year = year
		self.games = []
		self.teams = []
		self.players = []

	"""
	Add a game to the list of games played this season.
	"""
	def addGame(self, game):
		self.games.append(game)

	"""
	Add a team to the season. To make sure there are no duplicates, first
	checks if the team exists; this returns either the newly created team
	or the previously existing team.
	"""
	def addTeam(self, teamName):
		team = self.getTeamByName(teamName)
		if not team:
			team = Team(teamName)
			self.teams.append(team)
		return team

	"""
	Get a team that played this season, by the team's name.
	"""
	def getTeamByName(self, teamName):
		for team in self.teams:
			if team.name == teamName:
				return team
		else:
			return None

	"""
	Add a player to the season roster. To make sure there are no duplicates,
	first checks if the player exists; this returns either the newly created player
	or the previously existing player.
	"""
	def addPlayer(self, playerId, playerName):
		player = self.getPlayerById(playerId)
		if not player:
			player = Player(playerId, playerName)
			self.players.append(player)
		return player

	"""
	Get a player who played this season, by his player id.
	"""
	def getPlayerById(self, playerId):
		for player in self.players:
			if player.playerId == playerId:
				return player
		else:
			return None

	"""
	Analyze all the games played this season, and calculate the actual and optimum
	points for and against each team.
	Also calculate the players who scored above their average against each team.
	"""
	def analyzeGames(self):
		for game in self.games:
			# add teams from this game
			[ awayTeamName, homeTeamName ] = game.teams.keys()
			awayTeam = self.addTeam(awayTeamName)
			homeTeam = self.addTeam(homeTeamName)

			# get the team scores
			awayTeamScore = game.teams[awayTeamName]
			homeTeamScore = game.teams[homeTeamName]

			# record actual points
			awayTeam.actualPointsFor += awayTeamScore.actualPoints
			awayTeam.actualPointsAgainst += homeTeamScore.actualPoints
			homeTeam.actualPointsFor += homeTeamScore.actualPoints
			homeTeam.actualPointsAgainst += awayTeamScore.actualPoints

			# record optimum points
			awayTeam.optimumPointsFor += awayTeamScore.optimumPoints
			awayTeam.optimumPointsAgainst += homeTeamScore.optimumPoints
			homeTeam.optimumPointsFor += homeTeamScore.optimumPoints
			homeTeam.optimumPointsAgainst += awayTeamScore.optimumPoints

			# get the players who scored above average in this game for each team
			for playerScore in awayTeamScore.players:
				player = self.getPlayerById(playerScore.playerId)
				line = player.getAboveAverageWeeklyPointsLine(playerScore.week)
				if line:
					homeTeam.addAboveAverageOpposingPlayerPointsLine(line)
			for playerScore in homeTeamScore.players:
				player = self.getPlayerById(playerScore.playerId)
				line = player.getAboveAverageWeeklyPointsLine(playerScore.week)
				if line:
					awayTeam.addAboveAverageOpposingPlayerPointsLine(line)

	"""
	Analyze all the teams in the league for all the weeks that have been
	parsed this season. Calculate their actual and optimum record.
	"""
	def analyzeTeams(self):
		for game in self.games:
			[ awayTeamName, homeTeamName ] = game.teams.keys()
			awayTeam = self.addTeam(awayTeamName)
			homeTeam = self.addTeam(homeTeamName)

			# get the actual winner of this game
			if game.actualWinner == awayTeam.name:
				awayTeam.actualWins += 1
				homeTeam.actualLosses += 1
			elif game.actualWinner == homeTeam.name:
				awayTeam.actualLosses += 1
				homeTeam.actualWins += 1
			else:
				awayTeam.actualTies += 1
				homeTeam.actualTies += 1

			# get the optimum winner of this game
			if game.optimumWinner == awayTeam.name:
				awayTeam.optimumWins += 1
				homeTeam.optimumLosses += 1
			elif game.optimumWinner == homeTeam.name:
				awayTeam.optimumLosses += 1
				homeTeam.optimumWins += 1
			else:
				awayTeam.optimumTies += 1
				homeTeam.optimumTies += 1

	"""
	Analyze all the players who were on a roster this season, and their scores,
	calculating averages, etc.
	"""
	def analyzePlayers(self):
		for game in self.games:
			for teamScoreLine in game.teams.values():
				for playerLine in teamScoreLine.players:
					player = self.addPlayer(playerLine.playerId, playerLine.name)
					player.addScoreLine(playerLine)

		for player in self.players:
			player.analyzeScores()

	"""
	Calculate which players scored above average for your bench, and below averge in your starting lineup.
	"""
	def analyzeTeamPlayers(self):
		for game in self.games:
			[ awayTeamName, homeTeamName] = game.teams.keys()
			awayTeam = self.addTeam(awayTeamName)
			homeTeam = self.addTeam(homeTeamName)

			awayTeamScoreLine = game.teams[awayTeamName]
			homeTeamScoreLine = game.teams[homeTeamName]

			for playerScoreLine in awayTeamScoreLine.players:
				player = self.getPlayerById(playerScoreLine.playerId)
				pointsLine = PlayerPointsLine(player, playerScoreLine)

				if pointsLine.isHighScoringBenchPlayer():
					awayTeam.addHighScoringBenchPlayerPointsLine(pointsLine)
				elif pointsLine.isLowScoringStarter():
					awayTeam.addLowScoringStarterPlayerPointsLine(pointsLine)

			for playerScoreLine in homeTeamScoreLine.players:
				player = self.getPlayerById(playerScoreLine.playerId)
				pointsLine = PlayerPointsLine(player, playerScoreLine)

				if pointsLine.isHighScoringBenchPlayer():
					homeTeam.addHighScoringBenchPlayerPointsLine(pointsLine)
				elif pointsLine.isLowScoringStarter():
					homeTeam.addLowScoringStarterPlayerPointsLine(pointsLine)


	"""
	Analyze all the players, games, and teams for this season.
	"""
	def analyze(self):
		self.analyzePlayers()
		self.analyzeGames()
		self.analyzeTeams()
		self.analyzeTeamPlayers()

	"""
	Print the summary of points scored by each team, both actual and optimal.
	"""
	def printTeamPointsSummary(self):
		self.teams.sort(Team.sortByOptimumPointsForDescending)
		for team in self.teams:
			print "%s: APF: %d; APA: %d; OPF: %d; OPA: %d; dPF: %d; dPA: %d" % (team.name, team.actualPointsFor, team.actualPointsAgainst, team.optimumPointsFor, team.optimumPointsAgainst, team.optimumPointsFor - team.actualPointsFor, team.optimumPointsAgainst - team.actualPointsAgainst)

	"""
	Print the summary of each team's record, both actual and optimal.
	"""
	def printTeamRecordSummary(self):
		self.teams.sort(Team.sortByOptimumWinsDescending)
		for team in self.teams:
			print "%s: actual record: %d-%d-%d; optimum record: %d-%d-%d" % (team.name, team.actualWins, team.actualLosses, team.actualTies, team.optimumWins, team.optimumLosses, team.optimumTies)

	"""
	Print a summary of the players who scored significantly above average for each team.
	Optionally display WHICH players scored above average, and how much above average they were.
	"""
	def printTeamAboveAverageOpposingPlayersSummary(self, showIndividualPlayers=False):
		for team in self.teams:
			print "%s: # opposing players above average: %d; total above average: %d" % (team.name, len(team.aboveAverageOpposingPlayerPointsLines), team.getTotalOpposingPlayersPointsAboveAverage())

			if showIndividualPlayers:
				for line in team.aboveAverageOpposingPlayerPointsLines:
					if line.weekPoints - line.averagePoints > 10:
						print "%s: points: %d; above average: %d" % (line.name, line.weekPoints, line.weekPoints - line.averagePoints)

	"""
	Print a summary of each player's scores.
	"""
	def printPlayerScoreSummary(self):
		for player in self.players:
			print "%s: total points: %d; average points: %f" % (player.name, player.totalPoints, player.averagePoints)

	"""
	Print a summary of the players on each team that scored well on the bench.
	"""
	def printHighScoringBenchPlayersSummary(self):
		for team in self.teams:
			print team.name
			for playerPointsLine in team.highScoringBenchPlayers:
				print "%s, week %d: %d" % (playerPointsLine.name, playerPointsLine.week, playerPointsLine.weekPoints)

	"""
	Print a summary of the players on each team that scored badly while starting.
	"""
	def printLowScoringStartersSummary(self):
		for team in self.teams:
			print team.name
			for line in team.lowScoringStarters:
				print "%s, week %d: %d" % (line.name, line.week, line.weekPoints)

"""
Represents a single game in a single week, between two teams.
Reads and parses the HTML from the quick box score from that game,
and creates the team and player score lines. Determines who
won the game in reality, and who would have won if both teams had
been set optimally.
"""
class GameScore:
	def __init__(self, year, week, game):
		self.filename = '%s/%s/%s' % (year, week, game)
		self.year = year
		self.week = week
		self.game = game
		
		try:
			self.file = open(self.filename, 'r')
		except:
			self.file = None
			print "Could not read file: %s" % self.filename

		self.teams = {}

		self.actualWinner = ''
		self.optimumWinner = ''

		if self.file:
			self.analyzeFile()
			self.analyzeWinners()

	"""
	Determine who won in reality, and who would have won if both
	teams played optimally.
	"""
	def analyzeWinners(self):
		[ teamName1, teamName2 ] = self.teams.keys()

		team1 = self.teams[teamName1]
		team2 = self.teams[teamName2]

		if team1.actualPoints > team2.actualPoints:
			self.actualWinner = teamName1
		elif team2.actualPoints > team1.actualPoints:
			self.actualWinner = teamName2
		else:
			self.actualWinner = 'TIE'

		if team1.optimumPoints > team2.optimumPoints:
			self.optimumWinner = teamName1
		elif team2.optimumPoints > team1.optimumPoints:
			self.optimumWinner = teamName2
		else:
			self.optimumWinner = 'TIE'

	"""
	Parse the file and extract the player score lines for each player,
	and add them to the team score lines.
	"""
	def analyzeFile(self):
		teams = {}
		teamName = ''

		for line in self.file:
			# we can determine which team we're counting by the title above the list of scores
			teamNameSearch = re.search('<td.* class="tableHead">([\w\s\.]+)</td>', line)
			if teamNameSearch:
				teamName = teamNameSearch.group(1).replace(' BENCH', '')
				try:
					if not teams[teamName]:
						teams[teamName] = []
				except:
					teams[teamName] = []
				continue

			try:
				player = PlayerScoreLine(self.week, line)
				teams[teamName].append(player)
			except:
				continue

		for teamList in teams:
			self.teams[teamList] = TeamScoreLine(self.week, teams[teamList])

"""
Represents a single player's scoring line for a single game.
"""
class PlayerScoreLine:
	def __init__(self, week, line):
		self.line = line
		self.week = week
		if self._parsePlayerId(line):
			self.playerId = self._parsePlayerId(line)
			self.teamId = self._parseTeamId(line)
			( self.name, self.position ) = self._parseNameAndPosition(line)
			self.slot = self._parseSlot(line)
			self.points = self._parsePoints(line)
		else:
			raise Error("Cannot find player score")

	def __str__(self):
		return "week %s, player %s, team %s: %s, %s, %s, %s" % (self.week, self.playerId, self.teamId, self.name, self.position, self.slot, self.points)

	def _parsePlayerId(self, line):
		idSearch = re.search('id="plyr(\d+)"', line)
		if idSearch:
			return idSearch.group(1)
		else:
			raise Error("Cannot find playerId")

	def _parseTeamId(self, line):
		teamSearch = re.search('<div .* team_id="(\d+)"', line)
		if teamSearch:
			return teamSearch.group(1)
		else:
			raise Error("Cannot find team id")

	def _parseNameAndPosition(self, line):
		playerSearch = re.search('<div.+>([\w\s\.\/\'-]+)</div>\*?, \w+ ([\w\/]+)', line)
		if playerSearch:
			playerName = playerSearch.group(1)
			playerPosition = playerSearch.group(2)
			return (playerName, playerPosition)
		else:
			raise Error("Cannot find name and position")

	def _parseSlot(self, line):
		slotSearch = re.search('<td id="slot_\d+".*>([\w\/]+)</td><td', line)
		if slotSearch:
			return slotSearch.group(1)
		else:
			raise Error("Cannot find slot")


	def _parsePoints(self, line):
		pointsSearch = re.search('<td id="plscrg_\d+_totpts".*>(-?\d+)</td>', line)
		if pointsSearch:
			return int(pointsSearch.group(1))
		else:
			raise Error("Cannot find points")


	"""
	A comparison function to allow sorting players in a list
	by the number of points they scored, in descending order.
	"""
	def compareByPointsDescending(playerA, playerB):
		return cmp(playerB.points, playerA.points)

"""
Take a list of players for a given team in a given week, and calculate
their actual points scored as well as the number of points they'd have
scored if they set their roster optimally.
"""
class TeamScoreLine:
	def __init__(self, week, players=[]):
		self.week = week
		self.players = players
		self.actualPoints = 0
		self.benchPoints = 0
		self.irPoints = 0
		self.optimumPoints = 0

		self.analyzeActualPoints()
		self.analyzeBenchPoints()
		self.analyzeIRPoints()
		self.analyzeOptimumPoints()

	"""
	Calculate the number of points they actually scored with their
	starting lineup.
	"""
	def analyzeActualPoints(self):
		self.actualPoints = self.getPointsBySlots(['QB', 'RB', 'RB/WR', 'WR', 'TE', 'D/ST', 'K'])

	"""
	Calculate the number of points they scored on their bench.
	"""
	def analyzeBenchPoints(self):
		self.benchPoints = self.getPointsBySlots(['Bench'])

	"""
	Calculate the number of points the players on the IR scored.
	"""
	def analyzeIRPoints(self):
		self.irPoints = self.getPointsBySlots(['IR'])

	"""
	Calculate the number of points they would have scored if the lineup
	had been set optimally.
	Assumes that you can start 1 QB, 2 RB, 2 WR, 1 RB/WR, 1 TE, 1 D/ST, 1 K.
	Starts the top two RB, the top two WR, and the higher scoring of the third
	best in either category.
	"""
	def analyzeOptimumPoints(self):
		QBs = self.getPlayersByPositions(['QB'])
		RBs = self.getPlayersByPositions(['RB'])
		WRs = self.getPlayersByPositions(['WR'])
		TEs = self.getPlayersByPositions(['TE'])
		Ds = self.getPlayersByPositions(['D/ST'])
		Ks = self.getPlayersByPositions(['K'])

		self.optimumPoints = 0

		# they get the top score from their QB, TE, D/ST, and K
		if len(QBs) > 0:
			self.optimumPoints += QBs[0].points
		if len(TEs) > 0:
			self.optimumPoints += TEs[0].points
		if len(Ds) > 0:
			self.optimumPoints += Ds[0].points
		if len(Ks) > 0:
			self.optimumPoints += Ks[0].points

		# they get the top two scores from their RB
		if len(RBs) > 0:
			self.optimumPoints += RBs[0].points
		if len(RBs) > 1:
			self.optimumPoints += RBs[1].points
		
		# they get the top two scores from their WR
		if len(WRs) > 0:
			self.optimumPoints += WRs[0].points
		if len(WRs) > 1:
			self.optimumPoints += WRs[1].points

		# they get whichever score is higher from their third RB and third WR
		if len(RBs) > 2:
			thirdRB = RBs[2]
		else:
			thirdRB = None
		if len(WRs) > 2:
			thirdWR = WRs[2]
		else:
			thirdWR = None
		if thirdRB and thirdWR:
			if thirdRB.points > thirdWR.points:
				self.optimumPoints += thirdRB.points
			else:
				self.optimumPoints += thirdWR.points
		elif thirdRB:
			self.optimumPoints += thirdRB.points
		elif thirdWR:
			self.optimumPoints += thirdWR.points

	"""
	Get the number of points scored by all the players in the
	given slots.
	"""
	def getPointsBySlots(self, slots=[]):
		points = 0
		players = self.getPlayersBySlots(slots)
		for player in players:
			if player.slot in slots:
				points += player.points
		return points

	"""
	Get the players who were in the given slots.
	"""
	def getPlayersBySlots(self, slots=[]):
		players = []
		for player in self.players:
			if player.slot in slots:
				players.append(player)
		return players

	"""
	Get the players who play the given positions.
	"""
	def getPlayersByPositions(self, positions=[]):
		players =[]
		for player in self.players:
			if player.position in positions:
				players.append(player)

		players.sort(PlayerScoreLine.compareByPointsDescending)
		return players


